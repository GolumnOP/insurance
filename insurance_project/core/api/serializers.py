import datetime

from rest_framework import serializers

from core.models import Customer, Car, InsurancePolicy

"""
какие поля JSON,
какие из них read_only,
какая валидация нужна,
как переопределить create/update.
"""


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "full_name", "email", "phone"]


class CarSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Car
        fields = ["id", "customer", "vin", "model", "year"]


class InsurancePolicySerializer(serializers.ModelSerializer):
    car = CustomerSerializer(read_only=True)
    # GET /policies/1/ (вывод всей инфо о машине, а не только id)
    car_id = serializers.PrimaryKeyRelatedField(
        queryset=Car.objects.all(), write_only=True
    )

    # POST /policies/ при пост запросе указывается только id машины (машина уже существует в базе)

    class Meta:
        model = InsurancePolicy
        fields = ["id", "car", "policy_number",
                  "coverage_amount", "premium",
                  "start_date", "end_date",
                  "status", "car", "car_id"]
        read_only_fields = ["premium", "status"]

    def create(self, validated_data):
        car = validated_data.pop("car_id")

        age = datetime.datetime.now().year - car.year
        if age <= 3:
            coefficient = 0.05
        elif 4 <= age <= 10:
            coefficient = 0.08
        else:
            coefficient = 0.12

        validated_data["premium"] = validated_data["coverage_amount"] * coefficient
        validated_data["car"] = car
        validated_data["status"] = "AE"

        return super().create(validated_data)
