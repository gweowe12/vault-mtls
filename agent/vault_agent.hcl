pid_file = "pidfile"

auto_auth {
  method  {
    type = "approle"
    config = {
      role_id_file_path = "roleid"
      secret_id_file_path = "secretid"
    }
  }

  sink {
    type = "file"
    config = {
      path = "/tmp/vault_agent"
    }
  }
}

vault {
  address = "http://127.0.0.1:8200"
}

template {
  source      = "ca.tpl"
  destination = "../cert/ca.crt"
}

template {
  source      = "cert.tpl"
  destination = "../cert/server.crt"
}

template {
  source      = "key.tpl"
  destination = "../cert/server.key"
}
