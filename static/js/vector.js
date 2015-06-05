/*
**
**  VECTOR
** # Igor Shagadeev
   # shagastr@gmail.com
*/

function Vector(x, y) {
    this.x = x || 0;
    this.y = y || 0;
}

Vector.prototype.add = function (vector) {
    this.x += vector.x;
    this.y += vector.y;
}
Vector.prototype.substract = function (vector) {
    this.x -= vector.x;
    this.y -= vector.y;
}
function vector_sum(vector1, vector2) {
    var x = vector1.x + vector2.x;
    var y = vector1.y + vector2.y;
    return new Vector(x,y)
}
function vector_substract(vector1, vector2) {
    var x = vector1.x - vector2.x;
    var y = vector1.y - vector2.y;
    return new Vector(x,y)
}
function distance(vector1, vector2) {
    var x = vector1.x - vector2.x;
    var y = vector1.y - vector2.y;
    var v = new Vector(x,y);
    return v.getRoundMagnitude()
}
function vector_middle(vector1, vector2) {
    var x = (vector1.x + vector2.x)/2;
    var y = (vector1.y + vector2.y)/2;
    return new Vector(x,y)
}
Vector.prototype.normalize = function () {
//     var v_length = Math.round10(Math.pow(this.x * this.x + this.y * this.y, 0.5), -3);
//     this.x = Math.round10( this.x/v_length ,-3);
//     this.y = Math.round10( this.y/v_length ,-3);
    var v_length = Math.pow(this.x * this.x + this.y * this.y, 0.5).toFixed(3);
    this.x = (this.x/v_length).toFixed(3) ;
    this.y = (this.y/v_length).toFixed(3) ;
};
// Vector.prototype.round = function (e) {
//     this.x = Math.round10( this.x, e || -3)
//     this.y = Math.round10( this.y, e || -3)
//     this.x = parseFloat(this.x).toFixed(e || 3)
//     this.y = parseFloat(this.y).toFixed(e || 3)
// }
Vector.prototype.getMagnitude = function () {
    return Math.sqrt(this.x * this.x + this.y * this.y);
};
Vector.prototype.getRoundMagnitude = function () {
    return Math.round( Math.sqrt(this.x * this.x + this.y * this.y));
};
Vector.prototype.getAngle = function () {
    return Math.atan2(this.y, this.x);
};

Vector.prototype.fromAngle = function (angle, magnitude) {
    return new Vector(magnitude * Math.cos(angle), magnitude * Math.sin(angle));
};

Vector.prototype.mpl = function (k) {
    this.x = this.x*k;
    this.y = this.y*k;
};
/*   / VECTOR*/
