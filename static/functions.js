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
function updatePW() {
  passwdzero = $('#passwdzero').val();
  passwdone = $('#passwdone').val();
  passwdtwo = $('#passwdtwo').val();
  $.post("/auth/updatepw",{ passwdzero:passwdzero, passwdone:passwdone},function(data){
    if (data == 'error') {
      $('#status').replaceWith("Incorrect password.");
      return false;
    } else {
      $('#status').text("Password updated successfully.");
      return true;
    }
  });
}
function countChar(val) {
    var len = val.value.length;
    if (len >= 160) {
      val.value = val.value.substring(0, 160);
    } else {
      $('#charNum').text(160 - len);
    }
}

// Turns 1 (951) 555-1212 to 19515551212
function uglifyNumber(number) {
  var re = /\((\d{3})\)\s(\d{3})-(\d{4})/;
  var rez = re.exec(number);
  if (!rez) {
        $("#alert-messages").text("failed parsing uglify.");
  } else {
      ugly = "1" + rez[1] + rez[2] + rez[3];
      return ugly;
  }
    return false;
}
