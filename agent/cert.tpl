{{- /* cert.tpl */ -}}
{{ with secret "pki/issue/server-dot-com" "common_name=gweowe.server.com" "ttl=5m" }}
{{ .Data.certificate }}{{ end }}
