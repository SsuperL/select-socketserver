#select模拟socketserver
import select,queue,socket,json,os,sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Server(object):
    def __init__(self,addr,port):
        self.port=port
        self.addr=addr
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((addr,port))
        self.server.listen(5)
        self.server.setblocking(False)
        self.inputs=[self.server,]#一开始要先监测server，知道是否建立连接
        self.outputs=[]
        self.msg_dic={}
    def interative(self):
        while True:
            self.readable, self.writable, self.excetional = select.select(self.inputs, self.outputs, self.inputs)  # select 进行监听
            for r in self.readable:
                if r is self.server:#表示建立连接
                    conn,addr=self.server.accept()
                    conn.setblocking(False)#非阻塞
                    self.inputs.append(conn)#select监测连接过来的实例
                    '''新建立的连接还没发数据过来，现在就接收数据的话是空的，会报错，
                    因此要让select监测每一个连接过来的连接，这样才知道客户端发送数据过来'''
                    self.msg_dic[conn]=queue.Queue()#初始化一个队列，用于存放每一个连接的数据
                    print('建立连接',addr)
                else:
                    try:
                        data=r.recv(1024)#不可以直接判断数据是否为空，因为客户端断开时服务器已经接收不到数据了
                        self.msg_dic[r].put(data)
                        if r not in self.outputs:
                            self.outputs.append(r)  # 放入返回的连接队列里,下一次循环select检测的时候发给客户端
                    except ConnectionResetError as e:#处理没有数据的情况，即服务器断开
                        print(addr,' is close...')
                        if r in self.outputs:#移除连接
                            self.outputs.remove(r)
                        self.inputs.remove(r)
                        # r.close()
                        del self.msg_dic[r]
                        break
            for w in self.writable:
                try:
                    cmd=self.msg_dic[w].get_nowait()#从队列中取元素，不等待
                except queue.Empty:
                    # print('output queue for', w.getpeername(), 'is empty')
                    self.outputs.remove(w)
                else:
                    cmd_dic=json.loads(cmd.decode())
                    print(cmd_dic)
                    if cmd_dic['action']=='put':
                        filesize = cmd_dic['file_size']
                        filename = cmd_dic['filename']
                        received_size = 0
                        f = open(BASE_DIR + '/download/%s' % filename, 'wb')
                        while received_size < filesize:
                            if filesize-received_size>4096:
                                size=4096
                            else:
                                size=filesize-received_size
                            d=w.recv(size)
                            f.write(d)
                            received_size += len(d)
                        else:
                            print('文件下载完毕!')
                            f.close()

                    elif cmd_dic['action']=='get':
                        filename=cmd_dic['filename']
                        if os.path.exists(filename):
                            # w.send(b'True')
                            filesize=os.stat(filename).st_size
                            w.send(str(filesize).encode())
                            f=open(filename,'rb')
                            for line in f:
                                w.send(line)
                            else:
                                print('success')
                                f.close()
                        else:
                            w.sendall('文件不存在！'.encode('utf-8'))
                    # w.send(next_msg)
                # outputs.remove(w)#从outputs中移除旧的连接
            for e in self.excetional:#发生异常就将连接移除
                inputs.remove(e)
                if e in outputs:
                    self.outputs.remove(e)
                e.close()
                del msg_dic[e]#从队列中移除连接


port=3344
addr='localhost'
server=Server(addr,port)
server.interative()
