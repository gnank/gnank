#!/bin/sh
set -e
GNANK_DIR=`echo $0 | sed 's/[^\/]*$/src/g'`
export GNANK_DIR

codiAssigs=''

echo "0. Ejecutar Gnank directamente"
echo "1. Grau"
echo "2. Enginyeria Pla 2003"
echo "3. Master"
echo
echo -n "Escoge una opción [1,2,3] "

read choice
while [ $choice -ge 4 ]; do
    read choice
done

if [ $choice -eq 0 ]; then break
elif [ $choice -eq 1 ]; then
    codiAssigs='GRAU'
elif [ $choice -eq 2 ]; then
    echo "1. Enginyeria Superior"
    echo "2. Enginyeria Tec. Sistemes"
    echo "3. Enginyeria Tec. Gestió"
    echo
    echo -n "Escoge una opción [1,2,3] "

    read choice
    while [ $choice -ge 4 ]; do
        read choice
    done

    if [ $choice -eq 1 ]; then codiAssigs='EI03'
    elif [ $choice -eq 2 ]; then codiAssigs='ETS03'
    else codiAssigs='ETG03'
    fi
else
    echo "1. Computació"
    echo "2. Tecnologies de la Informació"
    echo "3. Inteligència Artificial"
    echo "4. Arquitectura de Computadors, Xarxes i Sistemes"
    echo "5. Erasmus Mundus en Computació Distribuida"
    echo
    echo -n "Escoge una opción [1,2,3,4,5] "

    read choice
    while [ $choice -ge 6 ]; do
        read choice
    done

    if [ $choice -eq 1 ]; then codiAssigs='MC'
    elif [ $choice -eq 2 ]; then codiAssigs='MTI'
    elif [ $choice -eq 3 ]; then codiAssigs='MIA'
    elif [ $choice -eq 4 ]; then codiAssigs='CANS'
    else codiAssigs='EMDC'
    fi
fi

exec $GNANK_DIR/gnank $codiAssigs
