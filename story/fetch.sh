# usage: fetch.sh listfile outdir ext
while read name path sig; do
  [ -z "$name" ] && continue
  [ -s "$2/$name.$3" ] && continue
  curl -sf --retry 3 -o "$2/$name.$3" "https://elevenlabsusercontent.com/database/workspace/e7d586086bb643a28e73db19db65d012/content_generation/$path/content.$3?Expires=${EXP:-1795147200}&KeyName=assets-cdn-key-1&Signature=$sig" || echo "FAIL $name"
done < "$1"
