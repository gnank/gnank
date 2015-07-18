#!/bin/sh

# Aquest script permet crear fitxers executables autocontinguts
# a partir del codi font del Gnank. S'ha d'executar des de la
# carpeta arrel del projecte.

set -e

TMPFILE=gnank.tar.gz
OUTPUT=gnank.sh

tar czf $TMPFILE src/gnank src/*.py src/*.png src/*.txt

{
	echo "#!/bin/sh"
	echo "TMPDIR=\$(mktemp -d /tmp/gnank.XXXXXX)"
	echo "tail -n +7 \$0 | tar xz -C \$TMPDIR"
	echo "\$TMPDIR/src/gnank"
	echo "rm -rf \$TMPDIR"
	echo "exit 0"

	cat $TMPFILE
} > $OUTPUT

chmod +x $OUTPUT

rm $TMPFILE
