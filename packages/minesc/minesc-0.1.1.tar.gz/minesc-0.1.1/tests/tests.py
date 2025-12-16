from msc2 import MineServerManager

msm = MineServerManager(servers_path='./servers')

print(msm.load_server_info('survivors'))