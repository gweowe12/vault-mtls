{{- /* cert-b.tpl */ -}}
{{ with secret "pki/issue/example-dot-com" "common_name=service-b.example.com" "ttl=2m" }}
{{ .Data.certificate }}{{ end }}