// # Igor Shagadeev
// # shagastr@gmail.com
// 
// 



/**
* @todo
* player_added - store field_size and calc positions
*
*/


/*
 * Global constants
 */
var user = {};
var host;
var ws;

function define_user(){
    user._xsrf = cookie("_xsrf");
    user.user_name = cookie("user_name");
    user.user__hash = cookie("user__hash");
    user.room = cookie("room");
    console.log('user', user)
}

function open_ws(){
/**
 * Initiate global websocket object.
 * @todo: Add user cookie for authentication.
 */
    host = location.origin.replace(/^http/, 'ws')
    ws = new WebSocket(host +"/socket/" + location.pathname.replace('/room/', '').replace('/', ''));
}


/**
 * Helper function to get the value of a cookie.
 */
function cookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


/*
 * Function to create a new message. from any text
 */
function postTextMessage(data) {
    var message = {data:data};
    message._xsrf = user._xsrf;
////    these will be recieved via cookie at server automatically
//     user.user_name;
//     user.user__hash;
//     user.room;
    
    // Send message using websocket.
    ws.send(JSON.stringify(message));

}





/**
 * Callback when receiving new messages.
 */
// updater = {}
// newMessages = function (data) {
//     var messages = data.messages;
//     if(messages.length == 0) return;
//     updater.cursor = messages[messages.length - 1]._id;
//     console.log(messages.length + "new messages, cursor: " + updater.cursor);
//     for (var i = 0; i < messages.length; i++) {
//         showMessage(messages[i]);
//     }
// };
/*
 * 
 */




/**
 * Function to add a bunch of (new) messages to the inbox.
 */
showMessage = function(message) {
//     if (log){ console.log("Show Message", message);}
    var str_message = JSON.stringify(message);
    $("#states").html(str_message);
};





/**
 * Function to send new mouse position every X sec.
 */

document.onmousemove = handleMouseMove;
var mousePos;
    
function handleMouseMove(event) {
    var canvasOffset=$("#world").offset();
    var offsetX=canvasOffset.left;
    var offsetY=canvasOffset.top;

    mousePos = {
        x: event.clientX-offsetX,
        y: event.clientY-offsetY
    };
}



/**
 * Function to getRandomName.
 */

var alpabet = 'qwertyuiopasdfghjklzxcvbnm1234567890'
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
function getRandomName( name_length) {
    var name = ''
    for (var i = 0; i< name_length; i++) {
        name+=alpabet[Math.floor(Math.random()*alpabet.length)]
    }
    return name
}





/**
 * 
 */
/**
 * game objects client
 */
/**
 * 
 */

/**
 *  Constants
 */
var max_speed = 10;
var iW = window.innerWidth;
var iH = window.innerHeight;



function Magnet(name, id, health,  position, unit_type) {
    this.orbit = 100;

    this.position = new Vector ( Math.random()*iW, Math.random()*iH );
    
    this.velocity = new Vector();

    this.style = {};
    this.health = health;
    this.name = name || getRandomName(5);
    this.unit_type = unit_type;
    this.id = id;

    this.dragging = false;
    this.connections = 0;
    this.size = Math.sqrt(this.health);

    this.style = {};
}
Magnet.prototype.draw = function(ctx){
    
    this.size = Math.sqrt(this.health);
    
    var b = this;
    var g =  b.unit_type;
    var style = b.style;
    
// // //          here we define    area size = b.size * 4
    c = ctx.createRadialGradient(b.position.x, b.position.y, 0, b.position.x, b.position.y, b.size * 4);
    c.addColorStop(0, style.glowA);
    c.addColorStop(1, style.glowB);

    ctx.font = '8pt Arial';
    ctx.fillStyle =  '#fff';
    ctx.fillText(b.name + b.unit_type, b.position.x - (b.name.length*7/2), b.position.y);
    
    ctx.font = '7pt Arial';
    ctx.fillStyle =  '#fff';
    ctx.fillText(b.health, b.position.x - b.size, b.position.y - b.size -10);
    
    
    ctx.beginPath();
    ctx.fillStyle = c;
    ctx.arc(b.position.x, b.position.y, b.size * 10, 0, Math.PI * 2, true);
    ctx.fill();
    
    ctx.beginPath();
    ctx.fillStyle = c;
    ctx.arc(b.position.x, b.position.y, b.size, 0, Math.PI * 2, true);
    ctx.fill();
    
    ctx.beginPath();
    ctx.strokeStyle = style.border;
    ctx.arc(b.position.x, b.position.y, b.size, 0, Math.PI * 2, true);
    ctx.stroke();
}
Magnet.prototype.vector_move = function () {
    var border = this.size;
    
    //change velocity
//     this.velocity
    
    
    this.position.add(this.velocity);
    //To prevent particles from moving out of the canvas
    // change velocity vector

    //top out
    if(this.position.y < border){this.velocity.y = 0;}
    //right out
    if(this.position.x > iW-border){this.velocity.x = 0;}
    //bottom out
    if(this.position.y > iH-border){this.velocity.y = 0;}
    //left out
    if(this.position.x < border){this.velocity.x = 0;}

    // change velocity vector
    //top out
    if(this.position.y < border){this.position.y += border;}
    //right out
    if(this.position.x > iW-border){this.position.x -= border;}
    //bottom out
    if(this.position.y > iH-border){this.position.y -= border;}
    //left out
    if(this.position.x < border){this.position.x += border;}

//     console.log('self.velocity',this.velocity);
//     console.log('self.position',this.position);

};






Wisps = new(function() {

    
    function z(name, id, health, position, unit_type) {
        var b = new Magnet(name, id, health, position, unit_type);
        b.position.x = position.x;
        b.position.y = position.y;
        b.unit_type = unit_type;
        b.style = k[unit_type];
        units.push(b);
    }


    function getMousePosition() {
        var pos = mousePos;
        if (!pos) {
            // We haven't seen any movement yet
        }
        else {
            // Use pos.x and pos.y
            var xy_data = {
                x : pos.x,
                y : pos.y
            }
            postTextMessage(xy_data )
        }
    }


    function drawMagnets() {
        
        if (k[g].useFade) {
            ctx.fillStyle = k[g].fadeFill;
            ctx.fillRect(0, 0, canvas.width, canvas.height)
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }

        for (var h=0; h < units.length; h++) {
//             units[h].vector_move();
            units[h].draw(ctx);
        }

    }
    
    //TODO
    function onresize() {
    
        
    }
    
    
    
    var r = navigator.userAgent.toLowerCase().indexOf("android") != -1 || navigator.userAgent.toLowerCase().indexOf("iphone") != -1 || navigator.userAgent.toLowerCase().indexOf("ipad") != -1

    var F = 20;
    var p = 300;
    var canvas, ctx, q = [];
    //f = units
    var units = [];

    var w = false;
    var x = 0;
    var g = 1;
    var k = [{
            //0
            glowA: "rgba(233,143,154,0.3)",
            glowB: "rgba(0,143,154,0.0)",
            border: "rgba(233,143,154,0.5)",
            particleFill: "#ffffff",
//             fadeFill: "rgba(22,22,22, 0.6)",
            fadeFill: "#222222",
            useFade: false
        }, {
            //1
            glowA: "rgba(0,200,250,0.3)",
            glowB: "rgba(0,200,250,0.0)",
            border: "rgba(0,200,250,0.5)",
            particleFill: "#ffffff",
//             fadeFill: "rgba(22,22,22, 0.6)",
            fadeFill: "#222222",
            useFade: true
        }, {
            //2
            glowA: "rgba(230,0,0,0.3)",
            glowB: "rgba(230,0,0,0.0)",
            border: "rgba(230,0,0,0.5)",
            particleFill: "#ffffff",
//             fadeFill: "rgba(11,11,11, 0.6)",
            fadeFill: "#222222",
            useFade: true
        }, {
            //3
            glowA: "rgba(0,230,0,0.3)",
            glowB: "rgba(0,230,0,0.0)",
            border: "rgba(0,230,0,0.5)",
            particleFill: "rgba(0,230,0,0.7)",
//             fadeFill: "rgba(22,22,22, 0.6)",
            fadeFill: "#222222",
            useFade: true
        }, {
            //4
            glowA: "rgba(0,0,0,0.3)",
            glowB: "rgba(0,250,0,0.0)",
            border: "rgba(0,250,0,0.5)",
//             particleFill: "#333333",
// //             fadeFill: "rgba(255,255,255,.6)",
//             fadeFill: "rgba(22,22,22, 0.6)",
            fadeFill: "#222222",
            useFade: true
        }, {
            //5
            glowA: "rgba(0,0,255,0.3)",
            glowB: "rgba(0,0,255,0.0)",
            border: "rgba(0,0,255,0.5)",
//             particleFill: "#333333",
//             fadeFill: "rgba(255,255,255, 0.6)",
            fadeFill: "#222222",
            useFade: true
        }, {
            //6
            glowA: "rgba(230,230,230,0.2)",
            glowB: "rgba(230,230,230,0.0)",
            border: "rgba(230,230,230,0.5)",
//             particleFill: "#ffffff",
//             fadeFill: "rgba(22,22,22,0.0)",
            fadeFill: "#222222",
            useFade: true
        }];



    this.init = function() {
        
        open_ws();
        
        define_user();
        
        /*
        *   WEB SOCKET fuunctions
        */
        
        // Websocket callbacks:
        ws.onopen = function() {
            console.log("Connected...");
        };
        ws.onmessage = function(event) {
            data = JSON.parse(event.data);
//             if(data.textStatus && data.textStatus == "unauthorized") {
//                 alert("unauthorized");
//             }
//             else if(data.error && data.textStatus) {
//                 alert(data.textStatus);
//             }
//             console.log("New Message", data);
//             if (data.messages) {
//                 newMessages(data)
//             } else {
//                 showMessage(data);
//             }
            
            try {
                console.log("msg "+data.type+" ", data);
                showMessage(data);
//                 console.log('data', data)
//                 console.log('units', units.length)
//                 console.log(data.user__hash)
                
                switch (data.type){
                    case 'move':{
                        // set new positions
                        for (var i = 0; i< units.length; i++){
                            if (units[i]['id'] == data.user__hash) {
//                                  console.log("New velocity", data.velocity.split(','));
                                var new_velocity = data.velocity.split(',');
                                var new_position = data.position.split(',');
                                
                                //get velocity - set new one
//                                 units[i].velocity = new Vector(parseFloat(new_velocity[0]), parseFloat(new_velocity[1]));
                                
                                //set new position
                                
                                units[i].position = new Vector(parseFloat(new_position[0]), parseFloat(new_position[1]));
                                
                                
                                //set new health
                                units[i].health = data.health;
                                
//                                 units[i].position.x = data.data.x;
//                                 units[i].position.y = data.data.y;
//                                 units[i].calc_velocity( new Vector(data.data.x, data.data.y) );
                            }
                        }
                        
                        console.log("units",units.length )
                        
                        break;
                    }
                    case 'add_user': {
                        console.log('start_position', data.start_position.split(','))
                        var start_position = data.start_position.split(',')

                        z(name = data.user_name,
                            id = data.user__hash,
                          health = data.health,
                            position = new Vector(parseInt(start_position[0]), parseInt(start_position[1])),
                                unit_type = 3);
                        break;
                    }
                    case 'dead': {
                        console.log('dead')

                        for (var i = 0; i< units.length; i++){
                            if (units[i]['id'] == data.user__hash) {
                                units.pop();
                            }
                        }
                        $("#choice_modal").modal();

                        break;
                    }

                }

            } catch (e) {
                console.log("error", e);
            }
        };
        ws.onclose = function() {
            // @todo: Implement reconnect.
            console.log("Closed!");
        };


        //e = canvas
        canvas = document.getElementById("world");

        if (canvas && canvas.getContext) {
            ctx = canvas.getContext("2d");
            if (r) {canvas.style.border = "none";}


            function resize() {
//                 i = r ? window.innerWidth : 800;
//                 j = r ? window.innerHeight : 550;
                canvas.width = iW;
                canvas.height = iH;
            }
            resize();

            loop();
            // INTERVAl for send message here every 40ms (update rate - 13ms=60fps)
            setInterval(getMousePosition, 30);
        }
    }
    
    
    function loop() {
        clear();
    //     update();
        drawMagnets();
    //     draw();
        queue();
    }

    function clear() {
    //     ctx.clearRect(0, 0, canvas.width, canvas.height);
    //         ctx.clearRect(0, 0, n, o);
    }

    function queue() {
        ////in case requestAnimationFrame cant be used  - another function  through setInterval
//         window.requestAnimationFrame ? window.requestAnimationFrame(loop) : setInterval(ba, 1E3 / 60);
        window.requestAnimationFrame(loop);
        
        
    }


    
});













$(document).ready(function() {
//     if (!window.console) window.console = {};
//     if (!window.console.log) window.console.log = function() {};

    
    define_user()
    
    //start dialog
    
    
    $("#choice_modal").modal();


    $("#unit_form").submit(function(e){
        e.preventDefault();
        console.log('go!')
        $("#connection").show();


        var form = $(this);

        $.ajax("http://127.0.0.1:8888/login", {
            error: function() {
                setTimeout(handshake, 1E3)
                console.log('error');
            },
            success: function(a) {
//                 a = a.split("\n");
//                 pa("ws://" + a[0])

                $("#choice_modal").modal('hide')
                Wisps.init();
                $("#connection").hide();

                //magnetic init
                //close modal
            },
            method: "GET",
            data: form.serialize(),

        })
        return false; 
    });




//      $("#choice_modal").modal('hide')
    
});




























