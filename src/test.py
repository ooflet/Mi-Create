startAngle = int(input("start angle: "))
endAngle = int(input("end angle: "))

def normalize_angle(angle):
    return (angle + 90) % 360 

def arc_length(start_angle, end_angle):
    print(start_angle, end_angle)
    # Normalize the angles to the range [0, 360)z
    start_angle = normalize_angle(start_angle)
    end_angle = normalize_angle(end_angle)
    print(start_angle, end_angle)
    
    # Calculate the difference
    difference = end_angle - start_angle
    
    # Adjust if the difference is negative (meaning the arc crosses the zero)
    if difference < 0:
        difference += 360
    
    return difference

print(normalize_angle(startAngle), arc_length(startAngle, endAngle))