// window.onload = function() {
// this.webRtcServer = new WebRtcStreamer("video", location.protocol + "//" + window.location.hostname + ":8000");
// webRtcServer.connect(url.video, url.audio, options);
// };
window.onbeforeunload = function() {
    if (this.webRtcServer != null) this.webRtcServer.disconnect();
};

$('#btn-stream').on('click', function(event) {
    // Toggle readonly: https://stackoverflow.com/questions/15637697/toggle-readonly-attribute-in-input-field
    // className: https://stackoverflow.com/questions/55766619/changing-the-style-of-a-html-button-within-a-javascript-function
    // innerHTML: https://stackoverflow.com/questions/56140202/how-to-change-text-inside-a-div-without-changing-any-other-element-in-the-div
    var prev = $(this).prev('input'),
        ro   = !prev.prop('readonly');
    prev.prop('readonly', ro).focus();
    if (ro) {
        classname = this.className;
        this.className = classname.replace("btn-success", "btn-danger");
        // this.className = "col-2 btn btn-icon btn-danger mb-2";
        this.innerHTML = `<i class="feather icon-slash"></i>`;
        var path = prev.val();
        url = {
            video: "rtsp://iauto:iauto@0.0.0.0:8554/" + path,
            audio: "rtsp://iauto:iauto@0.0.0.0:8554/" + path
            //video: "rtsp://iauto:iauto@amr.iauto-tech.com:8554/" + path,
            //audio: "rtsp://iauto:iauto@amr.iauto-tech.com:8554/" + path
        };
        options = "rtptransport=tcp";
        // var options = "rtptransport=tcp&timeout=60&width=640&height=0"
        window.webRtcServer = new WebRtcStreamer("video", location.protocol + "//" + window.location.hostname + ":8000");
        window.webRtcServer.connect(url.video, url.audio, options);
    } else {
        classname = this.className;
        this.className = classname.replace("btn-danger", "btn-success");
        // this.className = "col-2 btn btn-icon btn-success mb-2";
        this.innerHTML = `<i class="feather icon-check-circle"></i>`;
        // Destruct object: https://stackoverflow.com/questions/21118952/javascript-create-and-destroy-class-instance-through-class-method
        // Check is null or undefined: https://stackoverflow.com/questions/2559318/how-to-check-for-an-undefined-or-null-variable-in-javascript
        if (window.webRtcServer != null) {
            window.webRtcServer.disconnect();
            delete window.webRtcServer;
        }
    };
});
