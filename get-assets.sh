#!/usr/bin/env bash

set -e

if [[ -z $1 ]]
then
    echo "Provide emoji vendor name!"
    exit 1
fi
HD=$2
MORE_PNGS=$3

FOLDER=extra
PNG_PATH=$FOLDER/original
MAKE_1F491_1F48F=false
[[ $HD = true ]] && MAX_SIZE=160 || MAX_SIZE=96
SEP='_'

[[ $1 == 'facebook' || $1 == 'whatsapp' ]] && MAKE_1F491_1F48F=true

mkdir -p $PNG_PATH

declare -A skins
declare -A genders
declare -A apple_genders
declare -A kinds
declare -A handshakes

skins['d']=''
skins['0']='1f3fb'
skins['1']='1f3fc'
skins['2']='1f3fd'
skins['3']='1f3fe'
skins['4']='1f3ff'

genders['female']='1f469'
genders['male']='1f468'
genders['nogender']='1f9d1'

apple_genders['female']='w'
apple_genders['male']='m'
apple_genders['nogender']='n' # TODO: does not exist?

kinds['couple']=''
kinds['handshake']=''
kinds['heart']='2764'
kinds['kiss']='1f48b'

handshakes['l']='1faf1'
handshakes['r']='1faf2'

[[ $HD = true ]] && mkdir -p $FOLDER/160
mkdir -p $FOLDER/images/96 $FOLDER/images/64 $FOLDER/images/48 $FOLDER/images/40 $FOLDER/images/32 $FOLDER/images/20

echo "get-assets: Renaming PNGs..."
for kind in "${!kinds[@]}"
do
    if [[ $kind == 'handshake' ]]
    then
        for png in $(find $PNG_PATH/$kind -type f -name '*.png')
        do
            fname=$(basename $png)
            variant=$(cut -d'-' -f2 <<< ${fname/.png/})
            direction=$(cut -d'-' -f1 <<< ${fname/.png/})
            direction=${direction::1}
            skin=${skins[$variant]}
            [[ $skin != '' ]] && skin=${SEP}$skin
            oname=${handshakes[$direction]}$skin.$direction.png
            cp $png $FOLDER/images/$MAX_SIZE/$oname
        done
        magick $FOLDER/images/$MAX_SIZE/1faf1.l.png -fill gray -colorize 100 $FOLDER/images/$MAX_SIZE/silhouette${SEP}1faf1.l.png
        magick $FOLDER/images/$MAX_SIZE/1faf2.r.png -fill gray -colorize 100 $FOLDER/images/$MAX_SIZE/silhouette${SEP}1faf2.r.png
    else
        joiner=''
        joiner_value=${kinds[$kind]}
        [[ $joiner_value != '' ]] && joiner=${SEP}$joiner_value
        for gender in "${!genders[@]}"
        do
            category=$kind-$gender
            gender_value=${genders[$gender]}
            base_image=${gender_value}$joiner
            if [[ $kind == 'couple' ]]
            then
                output_image=silhouette.${apple_genders[$gender]}
            else
                output_image=silhouette${SEP}$gender_value$joiner.
            fi
            if [[ $category == 'couple-nogender' ]]
            then
                for left_skin in "${!skins[@]}"
                do
                    left_name=left-$left_skin.png
                    [[ $left_skin != 'd' ]] && left_skin=${SEP}${skins[$left_skin]}
                    for right_skin in "${!skins[@]}"
                    do
                        right_name=right-$right_skin.png
                        [[ $right_skin != 'd' ]] && right_skin=${SEP}${skins[$right_skin]}
                        out_name=1f9d1$left_skin${SEP}200d${SEP}1f91d${SEP}200d${SEP}1f9d1$right_skin.png
                        magick $PNG_PATH/$category/$left_name $PNG_PATH/$category/$right_name -compose over -composite $FOLDER/images/$MAX_SIZE/$out_name
                    done
                done
                oname=${gender_value}$skin$joiner.${direction::1}.png
                magick $PNG_PATH/$category/left-d.png -fill gray -colorize 100 $FOLDER/images/$MAX_SIZE/${output_image}l.png
                magick $PNG_PATH/$category/right-d.png -fill gray -colorize 100 $FOLDER/images/$MAX_SIZE/${output_image}r.png
            else
                for png in $(find $PNG_PATH/$category -type f -name '*.png')
                do
                    fname=$(basename $png)
                    variant=$(cut -d'-' -f2 <<< ${fname/.png/})
                    direction=$(cut -d'-' -f1 <<< ${fname/.png/})
                    skin=${skins[$variant]}
                    [[ $skin != '' ]] && skin=${SEP}$skin
                    oname=${gender_value}$skin$joiner.${direction::1}.png
                    cp $png $FOLDER/images/$MAX_SIZE/$oname
                done
                magick $FOLDER/images/$MAX_SIZE/$base_image.l.png -fill gray -colorize 100 $FOLDER/images/$MAX_SIZE/${output_image}l.png
                if [[ $kind != 'couple' ]]
                then
                    cp $FOLDER/images/$MAX_SIZE/$base_image.r.png $FOLDER/images/$MAX_SIZE/${output_image}r.png
                    HEART_PATH=$PNG_PATH/heart-$gender_value-$joiner_value.png
                    [[ ! -f $HEART_PATH ]] && HEART_PATH=$PNG_PATH/heart-$joiner_value.png # May cause unremoved bits
                    [[ ! -f $HEART_PATH ]] && HEART_PATH=$PNG_PATH/heart.png # May cause unremoved bits
                    magick composite -compose subtract $FOLDER/images/$MAX_SIZE/${output_image}r.png $HEART_PATH $FOLDER/images/$MAX_SIZE/${output_image}r.png
                    magick $FOLDER/images/$MAX_SIZE/$base_image.r.png -fill gray -colorize 100 PNG32:$FOLDER/images/$MAX_SIZE/${output_image}r.png
                    magick $FOLDER/images/$MAX_SIZE/${output_image}r.png $HEART_PATH -compose over -composite $FOLDER/images/$MAX_SIZE/${output_image}r.png
                else
                    magick $FOLDER/images/$MAX_SIZE/$base_image.r.png -fill gray -colorize 100 $FOLDER/images/$MAX_SIZE/${output_image}r.png
                fi
            fi
        done
    fi
done

if $MAKE_1F491_1F48F; then
    echo "Making 1f491 and 1f48f set..."
    declare -A codes
    codes['heart-nogender']='1f491'
    codes['kiss-nogender']='1f48f'
    for category in "${!codes[@]}"
    do
        code=${codes[$category]}
        for skin in "${!skins[@]}"
        do
            left_name=left-$skin.png
            right_name=right-$skin.png
            skin=${skins[$skin]}
            [[ $skin != '' ]] && skin=${SEP}$skin
            out_name=$code$skin.png
            magick $PNG_PATH/$category/$left_name $PNG_PATH/$category/$right_name -compose over -composite $FOLDER/images/$MAX_SIZE/$out_name
        done
    done
    unset codes
fi

if [[ $MORE_PNGS = true ]]
then
    echo "get-assets: Copying more PNGs..."
    cp -r $FOLDER/more/* $FOLDER/images/
fi

echo "get-assets: Resizing PNGs..."
[[ $HD = true ]] && mogrify -resize 160x160 -path $FOLDER/images/160 $FOLDER/images/96/*.png
mogrify -resize 64x64 -path $FOLDER/images/64 $FOLDER/images/96/*.png
mogrify -resize 40x40 -path $FOLDER/images/40 $FOLDER/images/64/*.png
# mogrify -resize 48x48 -path $FOLDER/images/48 $FOLDER/images/64/*.png
# mogrify -resize 40x40 -path $FOLDER/images/40 $FOLDER/images/48/*.png
# mogrify -resize 32x32 -path $FOLDER/images/32 $FOLDER/images/40/*.png
# mogrify -resize 20x20 -path $FOLDER/images/20 $FOLDER/images/32/*.png

echo "get-assets: Optimizing PNGs..."
pngquant --skip-if-larger -f --ext .png $FOLDER/images/*/*.png || true
oxipng -q $FOLDER/images/*/*.png

unset skins
unset genders
unset apple_genders
unset kinds
unset handshakes
