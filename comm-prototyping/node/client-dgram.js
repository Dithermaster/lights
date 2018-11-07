var unix = require('unix-dgram');



// prevent duplicate exit messages
var SHUTDOWN = false;

// Send a single message to the server.
//var message = Buffer('ping');
var message;


var client = unix.createSocket('unix_dgram');
client.on('error', console.error);
//client.send(message, 0, message.length, '/tmp/python_unix_sockets_example');

var self=this;

var stdin = process.openStdin();

console.log("input >");

stdin.addListener("data", function(d) {
    // note:  d is an object, and when converted to a string it will
    // end with a linefeed.  so we (rather crudely) account for that  
    // with toString() and then trim() 

    console.log("input > ");

    var inp = d.toString().trim();

    console.log("sent [" + 
        inp + "]");

    message = Buffer(inp);
    client.send(message, 0, message.length, '/tmp/python_unix_sockets_example');

  });


function cleanup(){
    if(!SHUTDOWN){ SHUTDOWN = true;
        console.log('\n',"Terminating.",'\n');
        client.close();
        process.exit(0);
    }
}
process.on('SIGINT', cleanup);


//client.close();
