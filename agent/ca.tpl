{{- /* ca.tpl */ -}}
{{ with secret "pki/issue/example-dot-com" "common_name=service.example.com" "ttl=2m" }}
{{ .Data.issuing_ca }}{{ end }}
