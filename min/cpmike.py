from calliope_mini import pin3,running_time,sleep
_g1=running_time()
def isClicked(level=10,rearm_time=500):
	A=False;global _g1
	if running_time()-_g1<rearm_time:sleep(10);return A
	B=pin3.read_analog()
	if B<518-level:_g1=running_time();return True
	return A