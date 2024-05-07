from base.models import Campus 
# for attendance model 
ATTENDANCE_CHOICE=[
        ('present','Present'),
        ('absent','Absent'),
        ('informed absent','Informed Absent'),
        ('tardy','Tardy'),
    ]

# for course offering and program offering 
OFFERING_CHOICES = [
        ('online', 'ONLINE'),
        ('micro cred', 'MICRO CRED'),
        ('blended', 'BLENDED'),
    ]

# for Weekly report model 
ENGAGEMENT_CHOICE=[
        ('na','N/A'),
        ('on track canvas','On Track - CANVAS'),
        ('on track assessment','On Track - Assessment'),
        ('on track learning activity','On Track - Learning Activity'),
        ('on track blended','On Track - Blended'),
        ('not engaged','Not Engaged'),
    ]
ACTION_CHOICE=[
        ('na','N/A'),
        ('follow up email and call','Follow Up Email and Call'),
        ('pastoral care','Pastoral Care'),
        ('personalized study plan/Extra session','Personalized Study Plan / Extra Session'),
        ('emergency contact','Emergency Contact'),
        ('other','Other'),
    ]
FOLLOW_UP_CHOICE=[
        ('na','N/A'),
        ('warning letter 1','Warning Letter 1'),
        ('warning letter 2','Warning Letter 2'),
    ]

PERFORMANCE_CHOICE=[
        ('na','N/A'),
        ('poor','POOR'),
        ('good','GOOD'),
        ('moderate','MODERATE'),
    ]

ASSESSMENT_CHOICE=[
        ('na','N/A'),
        ('making progress','MAKING PROGRESS '),
        ('no progress','NO PROGRESS'),
        ('request extension','REQUEST EXTENSION'),
        ('submitted','SUBMITTED'),
        ('not submitted','NOT SUBMITTED'),
        ('failed','FAILED'),
        ('re-sit','RE-SIT'),
    ]



# color choice list for models and css 
ATTENDANCE_COLOR_CHOICE = {
    'present': 'bg-green-500',
    'absent': 'bg-red-500',
    'informed absent': 'bg-yellow-500',
    'tardy': 'bg-blue-500'
}
LOCALITY_COLOR_CHOICE = {
    'domestic': 'bg-green-500',
    'international': 'bg-red-500',
}
FINAL_STATUS_COLOR_CHOICE = {
    'at risk': 'bg-red-500',
    'on track': 'bg-green-500',
}
ENGAGEMENT_COLOR_CHOICE = {
    'na': 'bg-orange-500',
    'on track canvas': 'bg-blue-500',
    'on track assessment': 'bg-green-500',
    'on track learning activity': 'bg-yellow-500',
    'on track blended': 'bg-purple-500',
    'not engaged': 'bg-red-500'
}

