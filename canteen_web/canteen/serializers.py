from django.contrib.auth.models import User, Group
from canteen.models import Report
from rest_framework import serializers

class ReportSerializer(serializers.HyperlinkedModelSerializer):
    date = serializers.ReadOnlyField()
    creator = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')
    creator_name = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Report
        fields = ('date', 'creator', 'creator_name', 'location', 'type', 'condition')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    group = serializers.ChoiceField(('Users', 'Workers', 'Managers', 'Admins'), write_only=True)
    reports = serializers.HyperlinkedRelatedField(view_name='report-detail', many=True, read_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'group', 'reports')

    def create(self, validated_data):
        u = User.objects.create_user(username=validated_data['username'],
                                     password=validated_data['password'])

        group = validated_data['group']
        if group == 'Admins':
            u.is_staff = True
            u.save()
        else:
            Group.objects.get(name=group).user_set.add(u)

        return u
