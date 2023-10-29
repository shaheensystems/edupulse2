def update_or_create_course(data):
    # Check if the program_code exits and doesn't contain spaces
    if data['student_course_code'] and  ' ' not in data['student_course_code']:
        try:
            linked_program=Program.objects.get(temp_id=data['student_course_code'])
            course = Course.objects.get(temp_id=data['student_course_code'])
            # If found, update the program_desc
            course.name = data['student_course_name']
            try:
                linked_program = Program.objects.get(temp_id=data['student_program_code'])
                course.program.add(linked_program)
            except Program.DoesNotExist:
                # Handle the case where the program doesn't exist
                print(f"Program with code '{data['student_course_code']}' not found")
            course.save()
            print("course updated successfully")
        except Course.DoesNotExist:
            # If not found, create a new program object
            Course.objects.create(temp_id=data['student_course_code'], name=data['student_course_name'])
            print("Course created successfully")
    else:
        print(f"Ignoring Course with code '{data['student_course_code']}' due to spaces in the code, not valid ")