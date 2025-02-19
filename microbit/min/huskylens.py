_E='Invalid model_id. Must be number in range [0,4]'
_D='Error: ID must be in range from 1 to 255.'
_C=None
_B=True
_A=False
from microbit import i2c,sleep,running_time
import math
_g1=['FaceRecognition','ObjectTracking','ObjectRecognition','LineTracking','ColorRecognition','TagRecognition','ObjectClassification','QRRecognition','BarcodeRecognition']
class Request_Command:KNOCK=44;ALGORITHM=45;ALL=32;BLOCKS=33;BLOCKS_LEARNED=36;BLOCKS_OF_ID=39;ARROWS=34;ARROWS_LEARNED=37;ARROWS_OF_ID=40;LEARNED=35;ALL_OF_ID=38;LEARN=54;FORGET=55;CUSTOM_LABEL=47;CUSTOM_TEXT=52;CLEAR_TEXT=53;SAVE_MODEL=50;LOAD_MODEL=51;SAVE_PHOTO=48;SAVE_SCREENSHOT=57;IS_PRO=59;VERSION=60
class Return_Code:ANY=1;OK=46;BUSY=61;INFO=41;BLOCK=42;ARROW=43;IS_PRO=59;NEED_PRO=62
class Algorithm:FACE_RECOGNITION=0;OBJECT_TRACKING=1;OBJECT_RECOGNITION=2;LINE_TRACKING=3;COLOR_RECOGNITION=4;TAG_RECOGNITION=5;OBJECT_CLASSIFICATION=6;QR_RECOGNITION=7;BARCODE_RECOGNITION=8
class Block:
	def __init__(A,x,y,width,height,id):A.x=x;A.y=y;A.width=width;A.height=height;A.id=id
	def _f2(A):return'Block: ID_'+str(A.id)+' Pos: ('+str(A.x)+' '+str(A.y)+') Size: ('+str(A.width)+' '+str(A.height)+')'
class Arrow:
	def __init__(A,x_tail,y_tail,x_head,y_head,id):A.x_tail=x_tail;A.y_tail=y_tail;A.x_head=x_head;A.y_head=y_head;A.id=id
	def get_direction(A):
		C=A.x_head-A.x_tail;D=A.y_head-A.y_tail;B=90-math.degrees(math.atan2(D,C))
		if B<0:B=B+360
		return int(B)
	def _f2(A):return'Arrow: ID_'+str(A.id)+' ('+str(A.x_tail)+' '+str(A.y_tail)+')->('+str(A.x_head)+' '+str(A.y_head)+')'
def byte_checksum(byte_list):return sum(byte_list)&255
def hexify(byte_array):
	A=byte_array
	if len(A)==0:return''
	return'0x'+''.join('{:02x}'.format(A)for A in A)
class Huskylens:
	I2C_ADDR=50
	def __init__(A):A.learned_slot_count=0;A.id_slots={};A.id_names={};A.algorithm=Algorithm.OBJECT_TRACKING;A.clear_texts();A.pro_enabled=A.is_pro()
	def initialize(A):
		B=_A
		for E in range(5):
			A.knock();B,F=A.get_response(Return_Code.OK)
			if B:break
		if B>0:
			C=A.clear_texts();D=A.set_algorithm(Algorithm.OBJECT_TRACKING)
			if C and D:print('Initialization successful!');return _B
			else:print("Initialization Failed. Couldn't change Algorithm");return _A
		else:print('Initialization Failed. Please check connection to Huskylens.');return _A
	def send_request(D,command,data=_C):
		B=data;A=bytearray(b'U\xaa\x11\x00\x00');A[3]=0 if B is _C else len(B);A[4]=command
		if B:
			for C in B:A.append(C)
		A.append(byte_checksum(A));i2c.write(Huskylens.I2C_ADDR,A);sleep(50)
	def get_response(K,return_code=Return_Code.ANY,timeout=500):
		C=return_code;A=bytearray(b'U\x00\x00\x00\x00');I=running_time()
		while running_time()-I<timeout:
			D=i2c.read(Huskylens.I2C_ADDR,1)[0]
			if D==85:break
		if D!=85:return-1,[]
		for J in range(4):A[J+1]=i2c.read(Huskylens.I2C_ADDR,1)[0]
		if A[0:3]!=b'U\xaa\x11':return-2,[]
		E=A[3];F=A[4];B=[]
		if E>0:G=i2c.read(Huskylens.I2C_ADDR,E+1);B=G[0:-1];H=G[-1]
		else:H=ord(i2c.read(Huskylens.I2C_ADDR,1))
		if H!=byte_checksum(list(A)+B):return-3,[]
		if C==Return_Code.ANY or F==C:return F,B
		else:return 0,B
	def knock(A):A.send_request(Request_Command.KNOCK)
	def set_algorithm(B,algorithm):
		A=algorithm
		if(A==Algorithm.QR_RECOGNITION or A==Algorithm.BARCODE_RECOGNITION)and not B.pro_enabled:raise RuntimeError('Error: Huskylens PRO version is required for algorithm ',_g1[A]);return _A
		D=[A,0];B.send_request(Request_Command.ALGORITHM,D);C,E=B.get_response(Return_Code.OK)
		if C>0:print('Current Algorithm:',_g1[A]);B.algorithm=A
		return _B if C>0 else _A
	def get_all(A):return A._f7(Request_Command.ALL)
	def get_all_learned(A):return A._f7(Request_Command.LEARNED)
	def get_all_with_id(A,id):
		if id<=0 or id>255:raise RuntimeError(_D)
		return A._f7(Request_Command.ALL_OF_ID,id)
	def get_one(A):B=A._f7(Request_Command.ALL);return A._f8(B)
	def get_one_learned(A):B=A._f7(Request_Command.LEARNED);return A._f8(B)
	def get_one_with_id(A,id):
		if id<=0 or id>255:raise RuntimeError(_D)
		B=A._f7(Request_Command.ALL_OF_ID,id);return A._f8(B)
	def attach_label(A,id,name):
		B=name
		if A.algorithm==Algorithm.OBJECT_TRACKING or A.algorithm==Algorithm.LINE_TRACKING:C=A._f6(1,B)
		elif A.algorithm==Algorithm.FACE_RECOGNITION or A.algorithm==Algorithm.TAG_RECOGNITION or A.algorithm==Algorithm.OBJECT_CLASSIFICATION or A.algorithm==Algorithm.OBJECT_RECOGNITION:
			D=A.id_slots.get(id)
			if D==_C:raise RuntimeError("Can't attach a name to an unlearned ID number")
			A.id_names[id]=B;C=_B
			for E in D:F=A._f6(E,B);C=C and F>0
		else:A.id_names[id]=B;C=A._f6(id,B)
		return _B if C>0 else _A
	def clear_labels(A):
		A.id_names.clear()
		for B in range(10):A._f6(B,'')
	def add_text(E,text,position_x,position_y):
		C=position_y;B=position_x;D=bytes(text,'utf-8')
		if len(D)>19:raise RuntimeError('Custom Text must be less than 20 bytes long.')
		if B>300 or B<0 or C<35 or C>240:raise RuntimeError("Custom Text can't be placed outside of screen pixel size.")
		A=[len(D)];A.append(255 if B>255 else 0);A.append(B%255);A.append(240-C);A.extend(list(D));E.send_request(Request_Command.CUSTOM_TEXT,A);F,G=E.get_response(Return_Code.OK);return _B if F>0 else _A
	def clear_texts(A):A.send_request(Request_Command.CLEAR_TEXT);B,C=A.get_response(Return_Code.OK);return _B if B>0 else _A
	def learn(A,id,name=_C):
		if id<=0 or id>255:raise RuntimeError('Parameter ID for learned item must be in range [0,255]')
		if A.algorithm==Algorithm.OBJECT_TRACKING or A.algorithm==Algorithm.LINE_TRACKING:id=1
		C=500
		if A.algorithm==Algorithm.OBJECT_CLASSIFICATION:C=1000
		A.send_request(Request_Command.LEARN,[id,0]);B,E=A.get_response(Return_Code.OK,C)
		if B>0:
			A.learned_slot_count+=1
			if not id in A.id_slots:A.id_slots[id]=[A.learned_slot_count]
			else:A.id_slots[id].append(A.learned_slot_count)
			D=A.id_names.get(id)
			if D!=_C:B=A.attach_label(A.learned_slot_count,D)
			elif name!=_C:B=A.attach_label(id,name)
		return _B if B>0 else _A
	def forget(A):
		A.send_request(Request_Command.FORGET);B,C=A.get_response(Return_Code.OK)
		if B:A.learned_slot_count=0;A.id_slots.clear()
		return _B if B else _A
	def save_photo(A):A.send_request(Request_Command.SAVE_PHOTO);B,C=A.get_response(Return_Code.OK,1000);return _B if B>0 else _A
	def save_screenshot(A):A.send_request(Request_Command.SAVE_SCREENSHOT);B,C=A.get_response(Return_Code.OK,1000);return _B if B>0 else _A
	def save_model(B,model_id):
		A=model_id
		if A<0 or A>4:raise RuntimeError(_E)
		B.send_request(Request_Command.SAVE_MODEL,[A,0]);C,D=B.get_response(Return_Code.OK,1000);print('Model saving: Check Huskylens screen for Result!\n\tModel name:',_g1[B.algorithm]+'_Backup_'+str(A)+'.conf');return _B if C>0 else _A
	def load_model(B,model_id):
		A=model_id
		if A<0 or A>4:raise RuntimeError(_E)
		B.send_request(Request_Command.LOAD_MODEL,[A,0]);C,D=B.get_response(Return_Code.OK,1000);print('Model Loading: Check Huskylens screen for Result!');return _B if C>0 else _A
	def is_pro(A):A.send_request(Request_Command.IS_PRO);B,C=A.get_response(Return_Code.IS_PRO);return bool(C[0])if B>0 else _A
	def _f6(C,id,name):
		A=bytes(name,'utf-8')
		if len(A)>19:raise RuntimeError('Custom Name must be less than 20 bytes long.')
		B=[id,len(A)+1];B.extend(list(A));B.append(0);C.send_request(Request_Command.CUSTOM_LABEL,B);D,E=C.get_response(Return_Code.OK);return _B if D>0 else _A
	def _f7(B,request_command,id=-1):
		I=_C if id<0 else[id,0];B.send_request(request_command,I);G,H=B.get_response(Return_Code.INFO)
		if not G:raise RuntimeError('Failed to request results. Got answer:'+str(G))
		J=H[0]+H[1]*255;C=0;D=[]
		while C<J:
			E,A=B.get_response(Return_Code.ANY)
			if E==Return_Code.BLOCK and B.algorithm!=3:K=A[0]+A[1]*255;L=240-A[2]+A[3]*255;M=A[4]+A[5]*255;N=A[6]+A[7]*255;F=A[8];O=Block(K,L,M,N,F);D.append(O);C+=1
			elif E==Return_Code.ARROW:P=A[0]+A[1]*255;Q=240-A[2]+A[3]*255;R=A[4]+A[5]*255;S=240-A[6]+A[7]*255;F=A[8];T=Arrow(P,Q,R,S,F);D.append(T);C+=1
			elif E==0:return[]
		return D
	def _f8(E,results):
		C=_C;D=440
		for A in results:
			B=0
			if E.algorithm==Algorithm.LINE_TRACKING:B=abs(A.x_tail+(A.x_tail-A.x_head)//2-160)+abs(A.y_tail+(A.y_tail-A.y_head)//2-120)
			else:B=abs(A.x-160)+abs(A.y-120)
			if B<D:C,D=A,B
		return C