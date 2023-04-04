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
  source      = "ca-a.tpl"
  destination = "../cert/ca.crt"
}

template {
  source      = "cert-a.tpl"
  destination = "../cert/service-a.crt"
}

template {
  source      = "key-a.tpl"
  destination = "../cert/service-a.key"
}

template {
  source      = "cert-b.tpl"
  destination = "../cert/service-b.crt"
}

template {
  source      = "key-b.tpl"
  destination = "../cert/service-b.key"
}