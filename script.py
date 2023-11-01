import re
import os
from paramiko import SSHClient, AutoAddPolicy, Transport, SFTPClient

class Script:
    def __init__(self, hostname, port, username, password, devopsNamespace):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.devopsNamespace = devopsNamespace
        self.sshClient = self.connect_ssh(self.hostname, self.port, self.username, self.password)
        self.sftpClient = self.connect_sftp(self.hostname, self.port, self.username, self.password)

    # 实例化ssh客户端、链接服务器
    def connect_ssh(self, hostname, port, username, password):
        sshClient = SSHClient()
        sshClient.set_missing_host_key_policy(AutoAddPolicy())
        sshClient.connect(hostname, port, username, password)
        return sshClient
    
    # 实例化 sftp 客户端、链接服务器
    def connect_sftp(self, hostname, port, username, password):
        sftpSock = Transport((hostname, port))
        sftpSock.connect(username=username, password=password)
        sftpClient = SFTPClient.from_transport(sftpSock)
        return sftpClient
    
    def close_ssh(self):
        self.sshClient.close()

    def close_sftp(self):
        self.sftpClient.close()

    # 获取容器名称
    def query_docker_id(self):
        _, sdtout, stderr = self.sshClient.exec_command(
        '''
        if [ -d "/data/jenkins/workspace/k8s-envs/{0}/opt" ];then
            cd /data/jenkins/workspace/k8s-envs/{0}/opt
            kubectl --kubeconfig=.kube_config.yaml -n={0} get pods
        else
            echo 流水线Namespace/IP: {0}, 输入错误
            exit 1
        fi
        '''.format(self.devopsNamespace))
            
        dockerIdList = []
        isFirstLine = True
        for line in sdtout.readlines():
            if isFirstLine:
                isFirstLine = False
                continue
            st = re.split(r"\s+", line)
            dockerIdList.append(st[0])
            
        stderrText = stderr.read().decode()
        return dockerIdList, stderrText
    
    # 打包、复制到服务器、下载到本地
    def to_package_download(self, dockerID, packageName, downloadPath):
        _, sdtout, stderr = self.sshClient.exec_command(
        '''
        cd /data/jenkins/workspace/k8s-envs/{0}/opt
        kubectl --kubeconfig=.kube_config.yaml -n={0} exec -it {1} -- tar -zcvf {2}.tar.gz ../
        kubectl --kubeconfig=.kube_config.yaml -n={0} cp {1}:{2}.tar.gz /tmp/pal/{2}.tar.gz
        kubectl --kubeconfig=.kube_config.yaml -n={0} exec -it {1} -- rm {2}.tar.gz
        '''.format(self.devopsNamespace, dockerID, packageName))
        
        stdoutText = sdtout.read().decode()
        stderrText = stderr.read().decode()
        if stderrText and stderrText.lower().find('error') > 0:
            return stdoutText, stderrText

        remotePath = "/tmp/pal/{0}.tar.gz".format(packageName)
        localPath = os.path.join(downloadPath, "./{0}.tar.gz".format(packageName))

        self.sftpClient.get(remotePath, localPath)
        self.sftpClient.remove(remotePath)

        return localPath, None