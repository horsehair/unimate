import json
from django.http import JsonResponse
from django.core.serializers import serialize

from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from knox.models import AuthToken
from users.serializers import *
from users.models import *

# Create your views here.
@api_view(['GET'])
def HelloUser(request):
    return Response("hello world!")



class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def get(self, request, *args, **kwargs):
        user = request.user

        if user == None or user.is_anonymous:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializers.CreateUserSerializer(user)
        
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        if len(request.data["username"]) < 4 or len(request.data["password"]) < 4:
            body = {"message": "short field"}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ProfileDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "user_id"
    queryset = Profile.objects.all()
    serializer_class = ProfileDetailSerializer

# 대학교 정보
class UniversityView(APIView):
    def get(self, request, *args, **kwargs):
        university = University.objects.all()
        serializer = UniversitySerializer(university, many=True)
        return Response(serializer.data)

# 단과대 정보
class CollegeView(APIView):
    def get(self, request, *args, **kwargs):
        university = University.objects.get(pk=kwargs['university_id'])
        college = College.objects.filter(university=university)
        serializer = CollegeSerializer(college, many=True)
        return Response(serializer.data)


# class AllCollegeView(APIView):
#     def get(self, request, *args, **kwargs):
#         user = request.user

#         if user == None or user.is_anonymous:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         college = College.objects.all()
#         serializer = serializers.CollegeSerializer(college, many=True)
#         return Response(serializer.data)

# 학과정보  
class MajorView(APIView):
    def get(self, request, *args, **kwargs):
        college = College.objects.get(pk=kwargs['college_id'])
        major = Major.objects.filter(college=college)
        serializer = MajorSerializer(major, many=True)
        return Response(serializer.data)


# class AllMajorView(APIView):
#     def get(self, request, *args, **kwargs):
#         user = request.user

#         if user == None or user.is_anonymous:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         major = Major.objects.all()
#         serializer = serializers.MajorSerializer(major, many=True)
#         return Response(serializer.data)


# 방 만들기
# class RoomCreateAPI(generics.CreateAPIView):
#     queryset = Room.objects.all()
#     serializer_class = RoomSerializer


class RoomCreateAPI(APIView):
    serializer_class = RoomSerializer
    
    def post(self, request):
        room_serializer = RoomSerializer(data=request.data)

        if room_serializer.is_valid():
            room_serializer.save()
            #room 정보 저장 후 입장시키기
            print(room_serializer.data['id'])
            print(request.user.id)
            person = User.objects.get(pk=request.user.id)
            room = Room.objects.get(pk=room_serializer.data['id'])
            room.owner.add(person)
            
            return Response(room_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(room_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 방 목록 - 최신순 정렬(기본)
class RoomListAPI(generics.ListAPIView):
    queryset = Room.objects.all().order_by('-created_at')
    serializer_class = RoomSerializer


# 대화 중인 채팅방 (owner가 안 불러와져서, RoomWithoutownerSerializer 작성)
class ParticipationListAPI(APIView):
    def get(self, request, format=None):
        queryset = User.objects.filter(pk=request.user.id).prefetch_related('room_set')[0].room_set.values()
        print(queryset)
        serializer = RoomWithoutownerSerializer(queryset, many=True)
        print(serializer)
        #return Response(status=status.HTTP_200_OK)
        return Response(serializer.data)


# 방 입장
class RoomEntranceAPI(APIView):
    def get_object(self, pk):
        return get_object_or_404(Room, pk=pk)

    def get(self, request, pk, format=None):
        print(request.user.id)
        room = self.get_object(pk)
        serializer = RoomSerializer(room)
        return Response(serializer.data)
    # 입장하기 (토큰 주인 대상)
    def post(self, request, pk):
        room = self.get_object(pk)
        person = User.objects.get(pk=request.user.id)
        room.owner.add(person)
        body = {"message": "Entrance complete"}
        return Response(body, status=status.HTTP_200_OK)


# 방 퇴장
class RoomExitAPI(APIView):
    def get_object(self, pk):
        return get_object_or_404(Room, pk=pk)

    def get(self, request, pk, format=None):
        print(request.user.id)
        room = self.get_object(pk)
        serializer = RoomSerializer(room)
        return Response(serializer.data)
    # 퇴장하기 (토큰 주인 대상)
    def post(self, request, pk):
        room = self.get_object(pk)
        roomuser = RoomUser.objects.filter(room_id=room.id, user_id=request.user.id)
        roomuser.delete()
        body = {"message": "Exit complete"}
        return Response(body, status=status.HTTP_200_OK)


