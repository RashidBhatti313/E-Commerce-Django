from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import filters

from .models import User, Product, Category, Order, Payment

from .serializers import UserSerializer, ProductSerializer, OrderSerializer, PaymentSerializer


def home_view(request):
    return JsonResponse({"message": "Welcome to the E-Commerce API! Use '/api/' routes to interact with the system."})


# class UserRegistrationViews(CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny]
#
#     def perform_create(self, serializer):
#         password = self.request.data.get("password")
#         try:
#             validate_password(password)
#         except ValidationError as e:
#             raise ValidationError({'password': e.messages})
#         user = serializer.save()
#         return user
#
#     def create(self, request, *args, **kwargs):
#         serialzer = self.get_serializer(data=request.data)
#         if serialzer.is_valid():
#             self.perform_create(serialzer)
#             return Response({
#                 'messages': 'Successfully Created',
#                 'user_id': serialzer.instance.id
#             }, status=status.HTTP_201_CREATED)
#         return Response(serialzer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"}, status=201)
    return Response(serializer.errors, status=400)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name']
    pagination_class = PageNumberPagination


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
