import os
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def get_request():
    return render_template('input.html')


@app.route("/hello")
def get_request2():
    return 'hello'


@app.route("/api/v1/ssh/create", methods=['POST'])
def ssh_create():
    params = request.get_json()
    project_id = params['project_id']
    floating_ip = params['floating_ip']
    port = params['port']

    dir_path = "/etc/nginx/servers-available"
    for path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, path)):
            with open(f"/etc/nginx/servers-available/{path}", "r", encoding='utf-8') as file:
                if file.read().find(port + ';') != -1:
                    # 중복되는 port 사용
                    return "ERROR: Same port already exists", 400

    content = (
        "server {\n"
        f"       listen      {port};\n"
        f"       proxy_pass  {floating_ip}:22;\n"
        "}\n"
    )
    with open(f"/etc/nginx/servers-available/{project_id}.conf", "a", encoding='utf-8') as file:
        file.write(content)
    os.system('sudo systemctl reload nginx')
    return "success", 200


@app.route("/api/v1/ssh/delete", methods=['POST'])
def ssh_delete():
    params = request.get_json()
    project_id = params['project_id']
    floating_ip = params['floating_ip']

    port = ''
    data = []
    with open(f"/etc/nginx/servers-available/{project_id}.conf", "r", encoding='utf-8') as file:
        block = [file.readline()]
        while (block[0] != ''):
            block += [file.readline()]
            block += [file.readline()]
            block += [file.readline()]
            if block[2].find(floating_ip + ':') == -1:
                data += block
            else:
                port = block[1].split()[1][:block[1].split()[1].find(';')]
            block = [file.readline()]

    if port == '':
        return "fail", 400

    with open(f"/etc/nginx/servers-available/{project_id}.conf", "w", encoding='utf-8') as file:
        for line in data:
            file.write(line)

    os.system('sudo systemctl reload nginx')
    return port, 200


@app.route("/api/v1/domain/create", methods=['POST'])
def domain_create():
    params = request.get_json()
    project_id = params['project_id']
    floating_ip = params['floating_ip']
    domain = params['domain']

    dir_path = "/etc/nginx/sites-enabled"
    for path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, path)):
            with open(f"/etc/nginx/sites-enabled/{path}", "r", encoding='utf-8') as file:
                if file.read().find(' '+domain + ';') != -1:
                    # 중복되는 domain 사용
                    return "ERROR: Same domain already exists", 400

    content = """server {
        server_name %s;
        location / {
            proxy_pass http://%s;
        }
}
""" % (domain, floating_ip)

    with open(f"/etc/nginx/sites-enabled/{project_id}", "a", encoding='utf-8') as file:
        file.write(content)
    os.system('sudo systemctl reload nginx')
    return "success", 200


@app.route("/api/v1/domain/delete", methods=['POST'])
def domain_delete():
    params = request.get_json()
    project_id = params['project_id']
    domain = params['domain']

    data = []
    with open(f"/etc/nginx/sites-enabled/{project_id}", "r", encoding='utf-8') as file:
        block = [file.readline()]
        while (block[0] != ''):
            block += [file.readline()]
            block += [file.readline()]
            block += [file.readline()]
            block += [file.readline()]
            block += [file.readline()]
            if block[1].find(' ' + domain + ';') == -1:
                data += block
            block = [file.readline()]

    with open(f"/etc/nginx/sites-enabled/{project_id}", "w", encoding='utf-8') as file:
        for line in data:
            file.write(line)

    os.system('sudo systemctl reload nginx')
    return "success", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
