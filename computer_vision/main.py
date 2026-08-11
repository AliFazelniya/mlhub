import cv2 as cv

cap = cv.VideoCapture(0)

window_name = "Live Filter"
cv.namedWindow(window_name, cv.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    filtered = cv.Canny(gray, 100, 200)
    cv.imshow(window_name, filtered)

    if cv.getWindowProperty(window_name, cv.WND_PROP_VISIBLE) < 1:
        break

    key = cv.waitKey(10) & 0xF
    if key == ord('q') or key == 27:
        break
    
cap.release()
cv.destroyAllWindows()

