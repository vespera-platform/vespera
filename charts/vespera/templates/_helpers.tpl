{{- define "vespera.securityContext" -}}
runAsNonRoot: true
allowPrivilegeEscalation: false
capabilities:
  drop: ["ALL"]
seccompProfile:
  type: RuntimeDefault
readOnlyRootFilesystem: true
{{- end }}