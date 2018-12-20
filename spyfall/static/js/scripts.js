var socket;
function join() {
    var nickname = document.getElementById("nickname").value;
    console.log(nickname);
    socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function() {
        socket.emit('receive_nickname', {nickname: nickname});
    });
    socket.on('before_start', function (data) {
        var names = data.names;
        $("#login").hide();
        $("#before").show();
        $("#start").show();
        $("#locations").empty();
        $("#names").empty();
        for (var i = 0; i < names.length; i++) {
            var name = names[i];
            $("#names").append("<p>" + name + "</p>");
        }
    });
    socket.on('role', function (data) {
        var name = data.name;
        var location = data.location;
        var locations = data.locations;
        console.log(data)
        $("#login").hide();
        $("#before").hide();
        $("#names").empty();
        $("#locations").empty();
        for (var i = 0; i < locations.length; i++) {
            let location = locations[i];
            $("#locations").append("<p>" + location + "</p>");
        }

        $("#start").show();
        $("#name").text(name);
        $("#location").text(location);
    });
}


function start() {
    socket.emit('start')
}
