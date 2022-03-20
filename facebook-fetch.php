<?php

// Based on https://github.com/iamcal/emoji-data/blob/master/build/facebook/grab.php

$codes = [
    '26f9-200d-2640', // found
    '2764-200d-1f525',
    '2764-200d-1fa79',
    '1f3cb-200d-2640', // found
    '1f3cc-200d-2640', // found
    '1f3f3-200d-26a7', // found
    '1f441-200d-1f5e8', // found
    '1f575-200d-2640', // found
    '1f62e-200d-1f4a8',
    '1f635-200d-1f4ab',
    '1f636-200d-1f32b-fe0f',
    '1f6dd',
    '1f6de',
    '1f6df',
    '1f7f0',
    '1f979',
    '1f9b0', // found
    '1f9cc',
    '1f9d1-200d-1f9b2',
    '1f9d1-1f3fb-200d-1f9b2',
    '1f9d1-1f3fc-200d-1f9b2',
    '1f9d1-1f3fd-200d-1f9b2',
    '1f9d1-1f3fe-200d-1f9b2',
    '1f9d1-1f3ff-200d-1f9b2',
    '1f9d1-1f3fb-200d-1f9b3',
    '1f9d1-1f3fc-200d-1f9b3',
    '1f9d1-1f3fd-200d-1f9b3',
    '1f9d1-1f3fe-200d-1f9b3',
    '1f9d1-1f3ff-200d-1f9b3',
    '1f9d4-200d-2640',
    '1fa7b',
    '1fa7c',
    '1faa9',
    '1faaa',
    '1faab',
    '1faac',
    '1fab7',
    '1fab8',
    '1fab9',
    '1faba',
    '1fac3',
    '1fac3-1f3fb',
    '1fac3-1f3fc',
    '1fac3-1f3fd',
    '1fac3-1f3fe',
    '1fac3-1f3ff',
    '1fac4-1f3fb',
    '1fac4-1f3fc',
    '1fac4-1f3fd',
    '1fac4-1f3fe',
    '1fac4-1f3ff',
    '1fac5-1f3fb',
    '1fac5-1f3fc',
    '1fac5-1f3fd',
    '1fac5-1f3fe',
    '1fac5-1f3ff',
    '1fad7',
    '1fad8',
    '1fad9',
    '1fae0',
    '1fae1',
    '1fae2',
    '1fae3',
    '1fae4',
    '1fae5',
    '1fae6',
    '1fae7',
    '1faf0',
    '1faf0-1f3fb',
    '1faf0-1f3fc',
    '1faf0-1f3fd',
    '1faf0-1f3fe',
    '1faf0-1f3ff',
    '1faf1',
    '1faf1-1f3fb',
    '1faf1-1f3fc',
    '1faf1-1f3fd',
    '1faf1-1f3fe',
    '1faf1-1f3ff',
    '1faf2',
    '1faf2-1f3fb',
    '1faf2-1f3fc',
    '1faf2-1f3fd',
    '1faf2-1f3fe',
    '1faf2-1f3ff',
    '1faf3',
    '1faf3-1f3fb',
    '1faf3-1f3fc',
    '1faf3-1f3fd',
    '1faf3-1f3fe',
    '1faf3-1f3ff',
    '1faf4',
    '1faf4-1f3fb',
    '1faf4-1f3fc',
    '1faf4-1f3fd',
    '1faf4-1f3fe',
    '1faf4-1f3ff',
    '1faf5',
    '1faf5-1f3fb',
    '1faf5-1f3fc',
    '1faf5-1f3fd',
    '1faf5-1f3fe',
    '1faf5-1f3ff',
    '1faf6',
    '1faf6-1f3fb',
    '1faf6-1f3fc',
    '1faf6-1f3fd',
    '1faf6-1f3fe',
    '1faf6-1f3ff',
];

foreach ($codes as $c) {
    fetch($c);
}

function fetch($code){
	fetch_single($code.'.png', null, 'EMOJI_3', 'facebook-extra', 32, 3);
}

function fetch_single($img, $alt_img, $type_key, $dir, $size, $ratio){
	$path = "./{$dir}/{$img}";

	// if (file_exists($path)) return;

	$types = array(
		'FBEMOJI' => 'f',
		'FB_EMOJI_EXTENDED' => 'e',
		'MESSENGER' => 'z',
		'UNICODE' => 'u',
		'COMPOSITE' => 'c',
		'EMOJI_3' => 't',
	);

	$type = $types[$type_key];

	$url = build_url($type, $size, $ratio, str_replace('-', '_', $img));

	if (try_fetch($url, $path)){
		return;
	}

	if ($alt_img){
		$url = build_url($type, $size, $ratio, str_replace('-', '_', $alt_img));

		if (try_fetch($url, $path)){
			return;
		}
	}
}

function build_url($type, $size, $pixelRatio, $img){
	$schemaAuth = "https://static.xx.fbcdn.net/images/emoji.php/v9";

	$path = $pixelRatio . '/' . $size . '/' . $img;
	$check = checksum($path);
	$url = $schemaAuth . '/' . $type . $check . '/' . $path;

	return $url;
}

function try_fetch($url, $path){
	http_fetch($url, $path);

	if (!file_exists($path)){
		return false;
	}

	if (!filesize($path)){
		@unlink($path);
		return false;
	}

	$fp = fopen($path, 'r');
	$sig = fread($fp, 4);
	fclose($fp);

	if ($sig != "\x89PNG"){
		@unlink($path);
		return false;
	}

	return true;
}
function encodeURIComponent($str) { /* a standard method in Javascript */
	return $str;
}
function unescape($str) {
	$trans = array('&amp;' => '&', '&lt;' => '<', '&gt;' => '>', '&quot;' => '"', '&#x27;' => "'");
	return strtr($str, $trans);
}
function checksum($subpath) {
	$checksumBase = 317426846;
	$base = $checksumBase;

	for ($pos = 0; $pos < strlen($subpath); $pos++) {
		$base = ($base << 5) - $base + ord(substr($subpath, $pos, 1));
		$base &= 4294967295;
	}
	return base_convert(($base & 255), 10, 16);
}

function http_fetch($url, $filename){
	$fh = fopen($filename, 'w');

	$options = array(
		CURLOPT_FILE	=> $fh,
		CURLOPT_TIMEOUT	=> 60,
		CURLOPT_URL	=> $url,
	);

	$options[CURLOPT_HTTPHEADER] = array(
		'Referer: https://www.facebook.com/',
		'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
	);

	$ch = curl_init();
	curl_setopt_array($ch, $options);
	curl_exec($ch);
	$ret = curl_getinfo($ch);
	curl_close($ch);

	fclose($fh);

    echo "({$ret['http_code']}) ($url)\n";
}