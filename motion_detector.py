#use Spacebar,Esc to close
import cv2,time
from datetime import datetime
import pandas


first_frame=None                 #for black part,Motion = difference in current frame and first frame
status_times=[None,None]          #to store motion in and out,None as want status_list[-2] initially
times=[]                         #times when status changes
df=pandas.DataFrame(columns=["Start","End"])        #for storing timings and generating graphs

face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
video=cv2.VideoCapture(0)

while True:
    isWorking,frame=video.read()
    status=0  #if object in frame status=0 else 1
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray=cv2.GaussianBlur(gray,(21,21),0) 	       #blur remove noise, (21,21)->width and height of gussian curve ,0->std deviation

    if first_frame is None:     #for first frame
        first_frame=gray
        continue        #so not run down code

    difference=cv2.absdiff(first_frame,gray)
    thresh_frame=cv2.threshold(difference,30,255,cv2.THRESH_BINARY)[1]        #if difference is 30 or more,255 put white
    thresh_frame-cv2.dilate(thresh_frame,None,iterations=10)  #to smooth the image, more iteration more smooth white area



    faces=face_cascade.detectMultiScale(gray,scaleFactor=1.05,minNeighbors=5)  #minNeighbors ideal value 5 to check how many near neighbour.
    for x,y,w,h in faces:
        frame=cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)  #(start cordinate),(end cordinate),(color of line),(width of rectangle)




  # find conters
    (contours,_)=cv2.findContours(thresh_frame.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)   #retr external gives external counters.(boundary points)
    #white area with area less than 1000 are not human or animal so ignore them
    #for motion detecting on the gray frame
    for contour in contours:
        if cv2.contourArea(contour)<1000:
            continue
        status=1   #when find frame of white color with more size status=1
        (x,y,w,h)=cv2.boundingRect(contour)
        cv2.rectangle(gray,(x,y),(x+w,y+h),(0,255,0),3)  #for contor of area>1000 show green boundary

    status_times.append(status)
    status_times=status_times[-2:]


    #check if status has change in 2 consecutive frame
    if status_times[-1]==1 and status_times[-2]==0:    #last 2 status are different store times
        times.append(datetime.now())
    if status_times[-1]==0 and status_times[-2]==1:    #last 2 status are different store times
        times.append(datetime.now())




#to show videos(frames)
    cv2.imshow("Capturing motion",gray)
    cv2.imshow("Capturing",frame)
    cv2.imshow("Threshold Frame",thresh_frame)
    


#code to stop detection when esc or spacebar is pressed
    key=cv2.waitKey(1)
    if(key==27 or key==32 or key==ord("\n")):
        if(status==1):
            times.append(datetime.now())
        break


for i in range(0,len(times),2):       #using pandas for data handling
    df=df.append({"Start":times[i],"End":times[i+1]},ignore_index=True)

df.to_csv("Times.csv")               #can view csv in excel for data viewing

print(times)
video.release()
cv2.destroyAllWindows()


