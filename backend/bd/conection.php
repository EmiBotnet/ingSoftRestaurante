<?php

class database{
    private $hostname = ""; //Nombre del host de la bd (localhost o si es en otra máquina, colocar la ip del dispositivo)
    private $database = ""; //Nombre de la base de datos
    private $user = ""; //Usuario de la bd
    private $password = ""; //Usuario de la bd
    private $charset = "utf8"; //Contraseña

    function conection(){

        try{
            $conection = "mysql=host:" . $this->hostname . "; dbname=" . $this->database . "; charset=" . $this->charset;
            $options = [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_EMULATE_PREPARES => FALSE
            ];
    
            $pdo = new PDO($conection,$this->user,$this->password,$options);
    
            return $pdo;
        }catch(PDOException $message){
            echo 'Error conection: ' . $message->getMessage();
            exit;
        }
      
    }
    
}

?>