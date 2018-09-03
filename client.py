import socket,json,os,sys,math
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Client():
    def __init__(self,addr,port):
        self.client = socket.socket()
        self.client.connect((addr, port))
    def interative(self):
        '''用户交互'''
        while True:
            cmd=input('command>>')#下达指令
            if len(cmd)==0:
                continue
            cmd_str=cmd.split()[0]#获取指令
            if hasattr(self,'%s'%cmd_str):
                func=getattr(self,'%s'%cmd_str)
                func(cmd)
            else:
                self.help()

    def help(self):
        message='''
        有效命令:
        put filename
        get filename
        '''
        print(message)

    def put(self,*args):
        '''上传文件到用户家目录'''
        cmd=args[0].split()
        if len(cmd)>1:
            filename=cmd[1]
            if os.path.isfile(filename):
                file_size=os.stat(filename).st_size
                cmd_dic={
                    'action':'put',
                    'filename':filename,
                    'file_size':file_size
                }
                self.client.send(json.dumps(cmd_dic).encode())
                f=open(filename,'rb')
                for line in f:
                    self.client.send(line)
                    size=f.tell()#用f.tell()来确定上传到哪个位置，即已上传的大小
                    self.process(size,file_size)
                f.close()
            else:
                print('文件不存在!')


    def get(self,*args):
        '''下载文件到dowload文件夹'''
        cmd=args[0].split()
        if len(cmd)>1:
            filename = cmd[1]
            cmd_dic={
                'action':'get',
                'filename':filename
            }
        self.client.send(json.dumps(cmd_dic).encode())
        file_size=self.client.recv(1024).decode()
        if file_size.isdigit()==False:
            print('文件不存在！')
        else:
            recv_size = 0
            file_size=int(file_size)
            if os.path.exists(BASE_DIR + '/download/%s' % filename):
                f = open(BASE_DIR + '/download/%s' % filename + '.new', 'wb')
            else:
                f = open(BASE_DIR + '/download/%s' % filename, 'wb')
            while recv_size < file_size:  # 数据大小比较
                data= self.client.recv(4094)  # 一次接收数据
                recv_size += len(data)  # 接收到的数据大小
                f.write(data)
                self.process(recv_size,file_size)
            else:
                print('receive done...')
                f.close()




    def process(self,size,file_size):
        '''显示进度条'''
        # percent='{:.2%}'.format(size/file_size)
        bar_length = 100  # 进度条长度,由空格和'=='组成
        percent = size/file_size
        hashes = '=' * int(percent * bar_length)  # 进度条显示的数量长度百分比
        spaces = ' ' * (bar_length - len(hashes))  # 定义空格的数量=总长度-显示长度
        sys.stdout.write(
            "\r[%s]%d%% " % ( hashes + spaces,percent*100))#percent*100:乘100后可以表示为百分数，%%：将%转义
        sys.stdout.flush()
        if size==file_size:
            # sys.stdout.write('\n上传成功！')
            sys.stdout.write('\n')

addr='localhost'
port=3344
client=Client(addr,port)
client.interative()



