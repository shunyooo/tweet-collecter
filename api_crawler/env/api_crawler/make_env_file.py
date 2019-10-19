import os

def make_env_file(save_path):
	with open(save_path, 'w') as out:
		hostname = 'HOSTNAME={}'.format(os.uname()[1])
		out.write(hostname)
		print('make env file: {}'.format(save_path))
		print(hostname)

if __name__ == '__main__':
	dir_path = os.path.dirname(os.path.realpath(__file__))
	save_path = os.path.join(dir_path, '.env')
	make_env_file(save_path)