$(document).ready(function() {

  // Make a navigation header active
  const accesslevels = window.location.pathname.split('/');

  if (accesslevels[1] === 'adm') {
    $('#nav-adm').addClass('active');
    $('#view-adm').addClass('active');

  } else if (accesslevels[1] === 'sup') {
    $('#nav-sup').addClass('active');
    $('#view-sup').addClass('active');

  } else if (accesslevels[1] === 'stu') {
    $('#nav-stu').addClass('active');
    $('#view-stu').addClass('active');
  }

});
