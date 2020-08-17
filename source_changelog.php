<?php
$changelog_json_file = "source_changelog.json";
$data = getopt(null, ["server:", "username:", "password:", "database:"]);
$db_login = mysqli_connect($data['server'], $data['username'], $data['password'], 'configs_'.$data['database']);
$changelog_query = "SELECT `changelog` from `common_config`";
$changelog = mysqli_query($db_login, $changelog_query) or die(mysqli_error($db_login));
$changelog = mysqli_fetch_assoc($changelog)['changelog'];

if (!is_file($changelog_json_file))
    file_put_contents($changelog_json_file, "");

$changelog_json = json_decode(file_get_contents($changelog_json_file), true);

if (isset($changelog) && $changelog != null)
    $changelog_json[$data['database']][date("d-m-Y")] = $changelog;

$changelog_json_write = fopen($changelog_json_file, "w") or die("Unable to open file");
fwrite($changelog_json_write, json_encode($changelog_json, JSON_PRETTY_PRINT));
fclose($changelog_json_write);
?>