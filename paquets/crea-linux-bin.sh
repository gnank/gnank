#!/bin/sh

# Aquest script permet crear fitxers executables autocontinguts a prtir
# del codi font del Gnank. S'ha de passar com a primer paràmetre el fitxer
# .tar.gz amb el codi font.

if [ -z $1 ]; then
	echo "Utilització: $0 GNANK_VERSIO.tar.gz"
	exit 0
fi

set -e

FILE=$1
DIR=`echo $FILE | sed 's/.tar.gz//' | sed 's/.*\///'`

echo "#!/bin/sh"
echo "TMPDIR=\`mktemp -d /tmp/gnank.XXXXXX\`"
echo "tail -n +7 \$0 | tar xz -C \$TMPDIR"
echo "\$TMPDIR/$DIR/gnank.sh"
echo "rm -rf \$TMPDIR"
echo "exit 0"

cat $FILE
