<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS, PUT, DELETE");
header("Access-Control-Allow-Headers: Content-Disposition, Content-Type, Content-Length, Accept-Encoding");
header("Content-type:application/json");

$json = file_get_contents("surveillantus_config.json");
// 文字エンコーディングの変換（文字化け対策）
$json = mb_convert_encoding($json, "UTF-8", "ASCII, JIS, UTF-8, EUC-JP, SJIS-WIN");
// JSONデータを連想配列に変換
$config = json_decode($json, true);

if($_SERVER["REQUEST_METHOD"] == "POST"){
    $data = array(
        "guild_id" => $_POST["guild_id"],
        "channel_id" => $_POST["channel_id"],
        "user_id" => $_POST["user_id"],
        "post_id" => $_POST["post_id"],
        "guild_name" => $_POST["guild_name"],
        "channel_name" => $_POST["channel_name"],
        "user_name" => $_POST["user_name"],
        "disp_name" => $_POST["disp_name"],
        "channel_topic" => $_POST["channel_topic"],
        "time" => $_POST["time"],
        "content" => $_POST["content"]
    );

    $link = mysqli_connect($config["host"], $config["user_name"],
            $config["password"],$config["database"]);
    if(!$link){
        die("データベースの接続に失敗しました");
    }

    $query="INSERT INTO `posts` VALUES ( ?, ?, ?, ?, ?, ? )";
    $stmt  = mysqli_prepare($link, $query);
    if($stmt){
        mysqli_stmt_bind_param($stmt,"ssssss",
        $data["post_id"],$data["guild_id"],$data["channel_id"],
        $data["user_id"],$data["time"],$data["content"]);
        mysqli_stmt_execute($stmt);
    }else{
        echo "Error: " . mysqli_error($link);
    }
    mysqli_stmt_close($stmt);// ステートメントを閉じる

    try{
        $query="INSERT INTO `guilds` VALUES ( ?, ? )";
        $stmt  = mysqli_prepare($link, $query);
        if($stmt){
            mysqli_stmt_bind_param($stmt,"ss",
            $data["guild_id"],$data["guild_name"]);
            mysqli_stmt_execute($stmt);
        }else{
            echo "Error: " . mysqli_error($link);
        }
        mysqli_stmt_close($stmt);// ステートメントを閉じる
    }catch(Exception $ex){
        $query="UPDATE `guilds` SET name=? WHERE id=? ;";
        $stmt  = mysqli_prepare($link, $query);
        if($stmt){
            mysqli_stmt_bind_param($stmt,"ss",
            $data["guild_name"],$data["guild_id"]);
            mysqli_stmt_execute($stmt);
        }else{
            echo "Error: " . mysqli_error($link);
        }
        mysqli_stmt_close($stmt);// ステートメントを閉じる
    }
    
    try{
        $query="INSERT INTO `channels` VALUES ( ?, ?, ? )";
        $stmt  = mysqli_prepare($link, $query);
        if($data["channel_topic"]==""){
            $data["channel_topic"]="No topics are found.";
        }
        if($stmt){
            mysqli_stmt_bind_param($stmt,"sss",
            $data["channel_id"],$data["channel_name"],$data["channel_topic"]);
            mysqli_stmt_execute($stmt);
        }else{
            echo "Error: " . mysqli_error($link);
        }
        mysqli_stmt_close($stmt);// ステートメントを閉じる
    }catch(Exception $ex){
        $query="UPDATE `channels` SET name=?, topic=? WHERE id=? ;";
        $stmt  = mysqli_prepare($link, $query);
        if($data["channel_topic"]==""){
            $data["channel_topic"]="No topics are found.";
        }
        if($stmt){
            mysqli_stmt_bind_param($stmt,"sss",
            $data["channel_name"],$data["channel_topic"],$data["channel_id"]);
            mysqli_stmt_execute($stmt);
        }else{
            echo "Error: " . mysqli_error($link);
        }
        mysqli_stmt_close($stmt);// ステートメントを閉じる
    }
    
    try{
        $query="INSERT INTO `users` VALUES ( ?, ?, ? )";
        $stmt  = mysqli_prepare($link, $query);
        if($stmt){
            mysqli_stmt_bind_param($stmt,"sss",
            $data["user_id"],$data["user_name"],$data["disp_name"]);
            mysqli_stmt_execute($stmt);
        }else{
            echo "Error: " . mysqli_error($link);
        }
        mysqli_stmt_close($stmt);// ステートメントを閉じる
    }catch(Exception $ex){
        $query="UPDATE `users` SET user_name=?, disp_name=? WHERE id=? ;";
        $stmt  = mysqli_prepare($link, $query);
        if($stmt){
            mysqli_stmt_bind_param($stmt,"sss",
            $data["user_name"],$data["disp_name"],$data["user_id"]);
            mysqli_stmt_execute($stmt);
        }else{
            echo "Error: " . mysqli_error($link);
        }
        mysqli_stmt_close($stmt);// ステートメントを閉じる
    }

    // 接続を閉じる
    mysqli_close($link);
}else{
    if(!isset($_GET["operation"])){return;}
    
    $link = mysqli_connect($config["host"], $config["user_name"],
            $config["password"],$config["database"]);
    if(!$link){
        die("データベースの接続に失敗しました");
    }
    
    #operationパラメータはデータの取得方法を指定する
    if($_GET["operation"]=="word2mes"){
        $word=$_GET["word"];
        $query = "SELECT * FROM `posts` WHERE content LIKE '%".$word."%' ORDER BY time DESC;";
        $stmt  = mysqli_prepare($link, $query);
        if($stmt){
            #mysqli_stmt_bind_param($stmt,"s",$word);
            mysqli_stmt_execute($stmt);
            // プリペアドステートメントに変数をバインドする
            mysqli_stmt_bind_result($stmt,$id,$guild_id,
                $channel_id,$user_id,$time,$content);
            $posts=[];
            while(mysqli_stmt_fetch($stmt)){
                array_push(
                    $posts,
                    array(
                        "post_id"=>$id,
                        "guild_id"=>$guild_id,
                        "channel_id"=>$channel_id,
                        "user_id"=>$user_id,
                        "time"=>$time,
                        "content"=>$content
                    )
                );                
            }
        }else{ echo "Error";return; }
        mysqli_stmt_close($stmt);
        $json_posts=json_encode(array("posts"=>$posts),JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT);
        echo $json_posts;
        // 接続を閉じる
        mysqli_close($link);
    }else if($_GET["operation"]=="word2user"){
        $word=$_GET["word"];
        $query = "SELECT * FROM `users` WHERE (user_name LIKE '%".$word."%'"
            ." OR disp_name LIKE '%".$word."%' );";
        $stmt  = mysqli_prepare($link, $query);
        if($stmt){
            #mysqli_stmt_bind_param($stmt,"s",$word);
            mysqli_stmt_execute($stmt);
            // プリペアドステートメントに変数をバインドする
            mysqli_stmt_bind_result($stmt,$id,$user_name,$disp_name);
            $users=[];
            while(mysqli_stmt_fetch($stmt)){
                array_push(
                    $users,
                    array(
                        "user_id"=>$id,
                        "user_name"=>$user_name,
                        "disp_name"=>$disp_name
                    )
                );                
            }
        }else{ echo "Error";return; }
        mysqli_stmt_close($stmt);
        $json_posts=json_encode(array("users"=>$users),JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT);
        echo $json_posts;
        // 接続を閉じる
        mysqli_close($link);   
    }else if(in_array($_GET["operation"],
            ["user2mes","chan2mes"])){
        if(isset($_GET["user_id"])){
            $user_id=$_GET["user_id"];
            $query = "SELECT * FROM `posts` WHERE author_id=? ORDER BY time DESC;";
            $stmt  = mysqli_prepare($link, $query);
            mysqli_stmt_bind_param($stmt,"s",$user_id);
        }else if(isset($_GET["channel_id"])){
            $channel_id=$_GET["channel_id"];
            $query = "SELECT * FROM `posts` WHERE channel_id=? ORDER BY time DESC;";
            $stmt  = mysqli_prepare($link, $query);
            mysqli_stmt_bind_param($stmt,"s",$channel_id);
        }
        
        if($stmt){
            mysqli_stmt_execute($stmt);
            // プリペアドステートメントに変数をバインドする
            mysqli_stmt_bind_result($stmt,$id,$guild_id,
                $channel_id,$user_id,$time,$content);
            $posts=[];
            while(mysqli_stmt_fetch($stmt)){
                array_push(
                    $posts,
                    array(
                        "post_id"=>$id,
                        "guild_id"=>$guild_id,
                        "channel_id"=>$channel_id,
                        "user_id"=>$user_id,
                        "time"=>$time,
                        "content"=>$content
                    )
                );                
            }
        }else{ echo "Error";return; }
        mysqli_stmt_close($stmt);
        $json_posts=json_encode(array("posts"=>$posts),JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT);
        echo $json_posts;
        // 接続を閉じる
        mysqli_close($link);   
    }else if(in_array($_GET["operation"],["id2user","serv2user"])){
        if($_GET["operation"]=="id2user"){
            $user_id=$_GET["user_id"];
            $query = "SELECT * FROM `users` WHERE id=?";
            $stmt  = mysqli_prepare($link, $query);
            mysqli_stmt_bind_param($stmt,"s",$user_id);
        }else if($_GET["operation"]=="serv2user"){
            $guild_id=$_GET["guild_id"];
            $query = "SELECT * FROM users WHERE id IN (SELECT author_id FROM `posts` WHERE guild_id=?);";
            $stmt  = mysqli_prepare($link, $query);
            mysqli_stmt_bind_param($stmt,"s",$guild_id);
        }

        if($stmt){
            mysqli_stmt_execute($stmt);
            // プリペアドステートメントに変数をバインドする
            mysqli_stmt_bind_result($stmt,$user_id,$user_name,
                $disp_name);
            $users=[];
            while(mysqli_stmt_fetch($stmt)){
                array_push(
                    $users,
                    array(
                        "user_id"=>$user_id,
                        "user_name"=>$user_name,
                        "disp_name"=>$disp_name
                    )
                );                
            }
        }else{ echo "Error";return; }
        mysqli_stmt_close($stmt);
        $json_posts=json_encode(array("users"=>$users),JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT);
        echo $json_posts;
        // 接続を閉じる
        mysqli_close($link);   
    }else if(in_array($_GET["operation"],["id2chan","serv2chan","word2chan"])){
        if($_GET["operation"]=="id2chan"){
            $channel_id=$_GET["channel_id"];
            $query = "SELECT * FROM channels WHERE id=?";
            $stmt  = mysqli_prepare($link, $query);
            mysqli_stmt_bind_param($stmt,"s",$channel_id);
        }else if($_GET["operation"]=="serv2chan"){
            $guild_id=$_GET["guild_id"];
            $query = "SELECT * FROM channels WHERE id IN (SELECT channel_id FROM `posts` WHERE guild_id=?);";
            $stmt  = mysqli_prepare($link, $query);
            mysqli_stmt_bind_param($stmt,"s",$guild_id);
        }else if($_GET["operation"]=="word2chan"){
            $word=$_GET["word"];
            $query = "SELECT * FROM channels WHERE ".
            "(id LIKE '%".$word."%'"
            ." OR topic LIKE '%".$word."%' "
            ." OR name LIKE '%".$word."%');";
            $stmt  = mysqli_prepare($link, $query);
        }

        if($stmt){
            mysqli_stmt_execute($stmt);
            // プリペアドステートメントに変数をバインドする
            mysqli_stmt_bind_result($stmt,$channel_id,$channel_name,
                $channel_topic);
            $channels=[];
            while(mysqli_stmt_fetch($stmt)){
                array_push(
                    $channels,
                    array(
                        "channel_id"=>$channel_id,
                        "channel_name"=>$channel_name,
                        "channel_topic"=>$channel_topic
                    )
                );
            }
        }else{ echo "Error";return; }
        mysqli_stmt_close($stmt);
        $json_posts=json_encode(array("channels"=>$channels),JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT);
        echo $json_posts;
        // 接続を閉じる
        mysqli_close($link);   
    }else if(in_array($_GET["operation"],["id2serv","word2serv"])){
        if($_GET["operation"]=="id2serv"){
            $guild_id=$_GET["guild_id"];
            $query = "SELECT * FROM guilds WHERE id=?";
            $stmt  = mysqli_prepare($link, $query);
            mysqli_stmt_bind_param($stmt,"s",$guild_id);
        }else if($_GET["operation"]=="word2serv"){
            $word=$_GET["word"];
            $query = "SELECT * FROM guilds WHERE ".
            "(id IN (SELECT guild_id FROM `posts` WHERE content LIKE '%".$word."%')"
            ." OR name LIKE '%".$word."%');";
            $stmt  = mysqli_prepare($link, $query);
        }

        if($stmt){
            mysqli_stmt_execute($stmt);
            // プリペアドステートメントに変数をバインドする
            mysqli_stmt_bind_result($stmt,$guild_id,$guild_name);
            $guilds=[];
            while(mysqli_stmt_fetch($stmt)){
                array_push(
                    $guilds,
                    array(
                        "guild_id"=>$guild_id,
                        "guild_name"=>$guild_name
                    )
                );
            }
        }else{ echo "Error";return; }
        mysqli_stmt_close($stmt);
        $json_posts=json_encode(array("guilds"=>$guilds),JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT);
        echo $json_posts;
        // 接続を閉じる
        mysqli_close($link);   
    }else if(in_array($_GET["operation"],["time2mes"])){
        if(isset($_GET["after"])){
            $time=$_GET["after"];
            $query = "SELECT * FROM posts WHERE `time`>=? ORDER BY time DESC;";
            $stmt  = mysqli_prepare($link, $query);
            mysqli_stmt_bind_param($stmt,"s",$time);
        }

        if($stmt){
            mysqli_stmt_execute($stmt);
            // プリペアドステートメントに変数をバインドする
            mysqli_stmt_bind_result($stmt,$id,$guild_id,
                $channel_id,$user_id,$time,$content);
            $posts=[];
            while(mysqli_stmt_fetch($stmt)){
                array_push(
                    $posts,
                    array(
                        "post_id"=>$id,
                        "guild_id"=>$guild_id,
                        "channel_id"=>$channel_id,
                        "user_id"=>$user_id,
                        "time"=>$time,
                        "content"=>$content
                    )
                );                
            }
        }else{ echo "Error";return; }
        mysqli_stmt_close($stmt);
        $json_posts=json_encode(array("posts"=>$posts),JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT);
        echo $json_posts;
        // 接続を閉じる
        mysqli_close($link);   
    }
}

?>