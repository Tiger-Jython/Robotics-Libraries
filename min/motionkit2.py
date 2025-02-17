from calliope_mini import*
i2c.init()
def motorR(dir,speed):buf_motor1=bytearray(3);buf_motor1[0]=0;buf_motor1[1]=dir;buf_motor1[2]=speed;i2c.write(16,buf_motor1)
def motorL(dir,speed):buf_motor2=bytearray(3);buf_motor2[0]=2;buf_motor2[1]=dir;buf_motor2[2]=speed;i2c.write(16,buf_motor2)
def led(right_left,on_off):
	buf_led=bytearray(2)
	if right_left==0:buf_led[0]=11
	else:buf_led[0]=12
	buf_led[1]=on_off;i2c.write(16,buf_led)
def rgbLed(red,green,blue):buf_rgbLed_red=bytearray(2);buf_rgbLed_red[0]=24;buf_rgbLed_red[1]=red;buf_rgbLed_green=bytearray(2);buf_rgbLed_green[0]=25;buf_rgbLed_green[1]=green;buf_rgbLed_blue=bytearray(2);buf_rgbLed_blue[0]=26;buf_rgbLed_blue[1]=blue;i2c.write(16,buf_rgbLed_red);i2c.write(16,buf_rgbLed_green);i2c.write(16,buf_rgbLed_blue)
def servoS1(angle):buf_servoS1=bytearray(2);buf_servoS1[0]=20;buf_servoS1[1]=angle;i2c.write(16,buf_servoS1)
def servoS2(angle):buf_servoS2=bytearray(2);buf_servoS2[0]=21;buf_servoS2[1]=angle;i2c.write(16,buf_servoS2)
def read_lineFollowR():i2c.write(16,bytearray([29]));data=i2c.read(16,1)[0];return 0 if data&1!=0 else 1
def read_lineFollowL():i2c.write(16,bytearray([29]));data=i2c.read(16,1)[0];return 0 if data&2!=0 else 1
def read_ultrasonic():i2c.write(16,bytearray([40]));sleep(20);data=i2c.read(16,2);distance=data[0]<<8|data[1];return distance
def read_infared():i2c.write(16,bytearray([43]));buf=i2c.read(16,4);data=buf[3]|buf[2]<<8|buf[1]<<16|buf[0]<<24;sleep(50);return data%1000;motorR(0,0);motorL(0,0);led(0,0);rgbLed(0,0,0);servoS1(0);servoS2(0);read_lineFollowR();read_lineFollowL();read_ultrasonic();read_infared()