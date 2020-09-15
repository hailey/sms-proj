function check_username(usrname) {
  $.ajax({
    method: "GET",
    url: "/checkUsername/" + usrname
  }).done(function(msg) {
    msgParsed = $.parseJSON(msg);
    if (msgParsed.error) {
      $('#usrError').text(msgParsed.error);
      return false;
    }
    if (msgParsed.name == 'Available') {
      $('#usrError').text('Username is available!');
      return true;
    } else {
      $('#usrError').text('Username already exists, please choose another.');
      return false;
      //Not available.
    }
  });
}
function checkEmail (email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
function checkPasswd () {
  $('#status').text('');
  passwdzero = $('#passwdzero').val();
  passwdone = $('#passwdone').val();
  passwdtwo = $('#passwdtwo').val();
  if (passwdone.length < 6 || passwdtwo.length < 6 || passwdzero.length < 6) {
    $('#status').text("The password length is too short. Six or more characters is required.");
    return false;
  } else {
    if (passwdone == passwdtwo) {
      $('#status').text("The passwords match!");
      return true;
    } else {
      $('#status').text("The password fields do not match!");
      return false;
    }
  }
}

function countChar(val) {
    var len = val.value.length;
    if (len >= 160) {
      val.value = val.value.substring(0, 160);
    } else {
      $('#charNum').text(160 - len);
    }
}
