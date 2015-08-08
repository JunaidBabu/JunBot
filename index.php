<?php
  echo "Umm..";
  echo "\r\n\n\n";
  $date = date('Y-m-d H:i:s');
  echo "\r\n".$date;
  $debug = file_get_contents('php://input');

  $result1 = file_get_contents('https://api.telegram.org/bot117344370:AAHHCNDsY6DGWdFBDNnk4e-KSVwXGOH09xU/sendMessage?text='.$date.'&chat_id=-17279035');
  $result2 = file_get_contents('https://api.telegram.org/bot117344370:AAHHCNDsY6DGWdFBDNnk4e-KSVwXGOH09xU/sendMessage?text='.$debug.'&chat_id=-17279035');
  
  echo "\r\n\n";
  echo "\r\n\n1" .$result1;
  echo "\r\n\n2" .$result2;
  echo "\r\n\n";
  echo "\r\n\nThe end";