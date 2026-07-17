from rest_framework import serializers
from .models import Vidskiptavinur, Kerfisnumer


class KerfisnumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kerfisnumer
        fields = ['id', 'item_id', 'lysing', 'er_virkur', 'stofnad', 'uppfaert']
        read_only_fields = ['stofnad', 'uppfaert']


class VidskiptavinurSerializer(serializers.ModelSerializer):
    kerfisnumer = KerfisnumerSerializer(many=True, read_only=True)
    heildar_greidslur = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )
    utistandandi_reikningar = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Vidskiptavinur
        fields = [
            'id', 'nafn', 'kennitala', 'customer_id', 'heimilisfang',
            'simanumer', 'netfang', 'vsk_numer', 'skuldastada',
            'heildar_greidslur', 'utistandandi_reikningar',
            'er_virkur', 'athugasemdir', 'kerfisnumer', 'stofnad', 'uppfaert'
        ]
        read_only_fields = ['customer_id', 'stofnad', 'uppfaert']


class VidskiptavinurListSerializer(serializers.ModelSerializer):
    """Einfaldari serializer fyrir lista"""
    
    class Meta:
        model = Vidskiptavinur
        fields = [
            'id', 'nafn', 'customer_id', 'kennitala', 'simanumer',
            'skuldastada', 'er_virkur'
        ]
