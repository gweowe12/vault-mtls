{{- /* key.tpl */ -}}
{{ with secret "pki/issue/server-dot-com" "common_name=gweowe.server.com" "ttl=5m" }}
{{ .Data.private_key }}{{ end }}
