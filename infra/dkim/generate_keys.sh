#!/usr/bin/env sh
set -eu

selector="${DKIM_SELECTOR:-mail}"
domain="${1:-example.com}"
outdir="$(dirname "$0")"
mkdir -p "${outdir}/keys/${domain}"

openssl genrsa -out "${outdir}/keys/${domain}/${selector}.private" 2048
openssl rsa -in "${outdir}/keys/${domain}/${selector}.private" -pubout -out "${outdir}/keys/${domain}/${selector}.public"

pub="$(tr -d '\n\r' < "${outdir}/keys/${domain}/${selector}.public" | sed 's/-----BEGIN PUBLIC KEY-----//;s/-----END PUBLIC KEY-----//')"
cat > "${outdir}/keys/${domain}/${selector}.txt" <<EOF
${selector}._domainkey IN TXT "v=DKIM1; k=rsa; p=${pub}"
EOF

echo "DKIM keys generated for ${domain} with selector ${selector}"
