"""
机器人API请求体生成器
用于生成各种机器人操作的请求数据
"""


class RobotAPIBody:
    """机器人API请求体生成器"""
    
    def gen_update_data(self,
                        robotId, user,
                        muteAudio=None,
                        muteVideo=None,
                        clientRole=None,
                        width=None,
                        height=None,
                        fps=None,
                        bitrate=None,
                        codecType=None,
                        dataStreamConfig=None):
        """
        生成更新机器人的请求数据
        
        Args:
            robotId: 机器人ID
            user: 用户名
            muteAudio: 静音音频
            muteVideo: 静音视频
            clientRole: 客户端角色
            width: 视频宽度
            height: 视频高度
            fps: 帧率
            bitrate: 码率
            codecType: 编解码类型
            dataStreamConfig: 数据流配置
            
        Returns:
            dict: 更新请求数据
        """
        update_data = {
            "robotId": robotId,
            "muteAudio": muteAudio,
            "muteVideo": muteVideo,
            "width": width,
            "height": height,
            "fps": fps,
            "clientRole": clientRole,
            "bitrate": bitrate,
            "codecType": codecType,
            "dataStreamConfig": dataStreamConfig,
            "user": user
        }
        return update_data

    def gen_create_data(self,
                        appId,
                        cname,
                        user,
                        uid=None,
                        userAccount=None,
                        privateParams=[],
                        url=None,
                        live=1,
                        clientRole=1,
                        codecType=2,
                        width=None,
                        height=None,
                        fps=None,
                        channelKey=None,
                        bitrate=None,
                        activeTime=None,
                        repeatTime=-1,
                        muteVideo=False,
                        muteAudio=False,
                        encryptionConfig=None,
                        autoSubscribe=False):
        """
        生成创建机器人的请求数据
        
        Args:
            appId: 应用ID
            cname: 频道名
            user: 用户名
            uid: 用户ID
            userAccount: 用户账号
            privateParams: 私有参数
            url: 视频URL
            live: 直播标识
            clientRole: 客户端角色
            codecType: 编解码类型
            width: 视频宽度
            height: 视频高度
            fps: 帧率
            channelKey: 频道密钥
            bitrate: 码率
            activeTime: 活跃时间
            repeatTime: 重复时间
            muteVideo: 静音视频
            muteAudio: 静音音频
            encryptionConfig: 加密配置
            autoSubscribe: 自动订阅
            
        Returns:
            dict: 创建请求数据
        """
        create_data = {
            "appId": appId,
            "cname": cname,
            "uid": uid,
            "userAccount": userAccount,
            "privateParams": privateParams,
            "url": url,
            "live": live,
            "clientRole": clientRole,
            "codecType": codecType,
            "width": width,
            "height": height,
            "fps": fps,
            "channelKey": channelKey,
            "bitrate": bitrate,
            "activeTime": activeTime,
            "repeatTime": repeatTime,
            "muteVideo": muteVideo,
            "muteAudio": muteAudio,
            "encryptionConfig": encryptionConfig,
            "autoSubscribe": autoSubscribe,
            "user": user
        }
        return create_data

    def gen_encryption_config(self,
                              encryptionMode=None,
                              encryptionKey=None,
                              encryptionKdfSalt=None,
                              datastreamEncryptionEnabled=None):
        """
        生成加密配置
        
        Args:
            encryptionMode: 加密模式
            encryptionKey: 加密密钥
            encryptionKdfSalt: 加密KDF盐
            datastreamEncryptionEnabled: 数据流加密是否启用
            
        Returns:
            dict: 加密配置
        """
        encryption_config = {
            "encryptionMode": encryptionMode,
            "encryptionKey": encryptionKey,
            "encryptionKdfSalt": encryptionKdfSalt,
            "datastreamEncryptionEnabled": datastreamEncryptionEnabled
        }
        return encryption_config

    def gen_datastream_config(self,
                              mode=None,
                              msg=None,
                              msgPrefix=None,
                              ts=None,
                              version=None):
        """
        生成数据流配置
        
        Args:
            mode (int): 数据流模式，取值范围为 [0, 3]
                0 - 停止数据流
                1 - 发送msg中的消息, 仅一次
                2 - 发送msgPrefix开头的、后面为时间戳的消息, 按照时间间隔(ts)重复发送
            msg (str): 数据流消息
            msgPrefix (str): 数据流消息前缀
            ts (int): 间隔时间
            version (int): dataStream版本号,取值范围为[0, 1]
            
        Returns:
            dict: 数据流配置
        """
        datastream_config = {
            "msgPrefix": msgPrefix,
            "ts": ts,
            "msg": msg,
            "mode": mode,
            "version": version
        }
        return datastream_config

    def gen_other_data(self, robotId, user):
        """
        生成其他操作的请求数据
        
        Args:
            robotId: 机器人ID
            user: 用户名
            
        Returns:
            dict: 请求数据
        """
        data = {
            "robotId": robotId,
            "user": user
        }
        return data

