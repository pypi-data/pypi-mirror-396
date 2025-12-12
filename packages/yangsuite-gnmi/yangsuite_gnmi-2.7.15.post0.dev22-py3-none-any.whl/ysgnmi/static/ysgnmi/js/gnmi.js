/**
 * Module for YANG Suite gNMI / gRPC client.
 */
let gnmi = function() {
    "use strict";

    /**
     * Default configuration of this module.
     */
    let config = {
        /* Selector string for a progressbar */
        progressBar: "#ys-progress",

        tree: "#tree",
        serviceDialog: "#gnmi-service-dialog",
        rpcOpGroup: '#ys-rpc-group',
        editOpClass: '.ytool-edit-op',
        rpcConfigClass: '.ys-cfg-rpc',
        rpcInfoTextarea: 'textarea#ys-gnmi-content',
        deviceSelect: '#ys-devices-replay',
        getType: '[name=ys-get-type]:checked',
        originType: '[name=ys-origin-type]:checked',
        otherOrigin: '#ys-origin-other',
        prefixSupport: '#ys-prefix',
        base64: '#ys-base64',
        encodingType: '[name=ys-encoding-type]:checked',
        subscribeMode: '[name=ys-subscribe-mode]:checked',
        subscribeSubMode: '[name=ys-subscribe-submode]:checked',
        sampleInterval: '#ys-sample-interval',
        rawGNMI: "textarea#ys-gnmi-content",
        ansibledialog:'div#ys-ansible',

        buildGetURI: '/gnmi/build_get/',
        buildSetURI: '/gnmi/build_set/',
        runURI: '/gnmi/run/',
        stopSessionURI: '/gnmi/stop/session/',
        runResultURI: '/gnmi/runresult/',
        runReplayURI: '/gnmi/runreplay/',
        showReplayURI: '/gnmi/showreplay/',
        getAnsibleURI: '/gnmi/getansible/',
    };

    let c = config;     // internal alias for brevity

    let winref = {}

    /**
     * getNamespaceModules
     *
     * Collect special gNMI tree {prefix: module name} object needed to convert
     * prefixes in Xpaths to module names.
     *
     * @param {Object} data: Configuration data for request.
     */
    function getNamespaceModules(data) {
        // First config node is sufficent (for one module, one gNMI message).
        let cfgEle = $(rpcmanager.config.rpcConfigClass)[0];
        if (!cfgEle) {
            alert("Cannot build JSON without values set in tree.");
            return;
        }
        let nodeId = cfgEle.getAttribute('nodeid');
        let node = $(c.tree).jstree(true).get_node(nodeId);
        let moduleid = node.parents[node.parents.length - 2];
        let module = $(c.tree).jstree(true).get_node(moduleid);
        Object.keys(data.modules).forEach(function(key) {
            data.modules[key]['namespace_modules'] = module.data.namespace_modules;
        });
    }

    function getXpathValues(data){
      let cfgEle = $(rpcmanager.config.rpcConfigClass)[0];
      if (!cfgEle) {
          alert("Cannot build JSON without values set in tree.");
          return;
      }
      // let nodeId = cfgEle.getAttribute('nodeid');
      // let node = $(c.tree).jstree(true).get_node(nodeId);
      // let moduleid = node.parents[node.parents.length - 2];
      // let module = $(c.tree).jstree(true).get_node(moduleid);
      //   // for (let rowCfg of Object.entries(modules[moduleName].configs)) {
      let data1 = []
      Object.keys(data.modules).forEach(function(key) {
          data1 = data.modules[key]['configs']
      });
      return data1
    }

    function buildJSON(device=null) {
        let data = rpcmanager.getRPCconfigs($(c.tree));
        getNamespaceModules(data);
        let operation = 'get'
        let action = $(config.rpcOpGroup + ' .selected').attr('data-value');
        let uri;
        if (action == 'get') {
            uri = config.buildGetURI;
            data['get_type'] = $(c.getType).val();
            operation = 'get'
        } else if (action == 'subscribe') {
            uri = config.buildGetURI;
            data['request_mode'] =  $(c.subscribeMode).val();
            data['sub_mode'] =  $(c.subscribeSubMode).val();
            data['sample_interval'] =  $(c.sampleInterval).val();
            operation = 'subscribe'
        } else if (action == 'set') {
            uri = config.buildSetURI;
            operation = 'edit-config'
        }
        let origin = "";
        origin = $(c.originType).val();
        if (origin == 'other') {
            origin = $(c.otherOrigin).val();
        }
        data['origin'] = origin;
        data['prefix'] = $(c.prefixSupport).prop("checked");
        data['device'] = device;
        data['encoding'] = $(c.encodingType).val();
        data['base64'] = $(c.base64).prop("checked");
        data['action'] = action;
        data['run'] = false;
        data['proto-op'] = operation;
        let rpc_data = {}
        rpc_data['gentype'] = data['get_type'];
        rpc_data['commit'] = '';
        rpc_data['prefix_namespaces'] = data['prefix'];
        rpc_data['segment'] = rpcmanager.config.segmentctr++;
        rpc_data['cfgd'] = data;
        rpcmanager.config.savedrpcs.push(rpc_data);
        jsonPromise(uri, data).then(function(retObj) {
            $(config.rpcInfoTextarea).val(retObj.gnmiMsgs);
        }, function(retObj) {
            popDialog("Error " + retObj.status + ": " + retObj.statusText);
        });
    };


    function runGNMI(device, data) {
        if (!device) {
            popDialog("Please select a device");
            return;
        }
        if (!$("textarea#ys-gnmi-content").val().trim()) {
            alert('"Build JSON" from tree or paste gNMI message in run frame.');
            return;
        }
        if (!data.raw) {
            data = rpcmanager.getRPCconfigs($(c.tree));
            getNamespaceModules(data);
            let origin = "";
            origin = $(c.originType).val();
            if (origin == 'other') {
                origin = $(c.otherOrigin).val();
            }
            data['origin'] = origin;
            data['prefix'] = $(c.prefixSupport).prop("checked");
            data['base64'] = $(c.base64).prop("checked");
            data['run'] = true;
            data['encoding'] = $(c.encodingType).val();
        }
        data['action'] = $(config.rpcOpGroup + ' .selected').attr('data-value');
        data['device'] = device;
        if (data['action'] == 'subscribe') {
            data['request_mode'] =  $(c.subscribeMode).val();
            data['sub_mode'] =  $(c.subscribeSubMode).val();
            data['sample_interval'] =  $(c.sampleInterval).val();
        }
        if (data['action'] == 'get') {
            data['get_type'] = $(c.getType).val()
        }

        $.when(jsonPromise(config.runURI + device, data))
        .then(function(retObj) {
            if (!retObj) {
                popDialog("<pre>RUN " + data['action'].toUpperCase() + " failed</pre>");
                if (winref.device) {
                    winref.device.close();
                    delete winref.device;
                }
                return;
            }
            if (retObj.response) {
                popDialog("<pre>" + retObj.response + "</pre>");
                if (winref.device) {
                    winref.device.close();
                    delete winref.device;
                }
                return;
            }
        })
        .fail(function(retObj) {
            popDialog("<pre>Status: " + retObj.status + "\n" + retObj.statusText + "</pre>");
            if (winref.device) {
                winref.device.close();
                delete winref.device;
            }
        });

        if (!winref.device) {
            winref[device] = window.open(
                config.runResultURI + device, device,
                "height=700 overflow=auto width=800, scrollbars=yes"
            );
        }
    };

    function runCapabilities(device, data) {
        if (!device) {
            popDialog("Please select a device");
            return;
        }

        let pb = startProgress($(config.progressBar)) || $(config.progressBar);

        return jsonPromise(config.runURI + device, data).then(function(retObj) {
            stopProgress(pb);
            return retObj;
        }, function(retObj) {
            stopProgress(pb);
            popDialog("Error " + retObj.status + ": " + retObj.statusText);
        });
    };

    function stopSession(device) {
        return jsonPromise(config.stopSessionURI + device);
    }

    function runReplay(device, data) {
        if (!device) {
            popDialog("Please select a device");
            return;
        }

        let pb = startProgress($(config.progressBar)) || $(config.progressBar);

        return jsonPromise(config.runReplayURI + device, data).then(function(retObj) {
            stopProgress(pb);
            return retObj;
        }, function(retObj) {
            stopProgress(pb);
            popDialog("Error " + retObj.status + ": " + retObj.statusText);
        });
    };

    function showReplay(data) {
        data['get_type'] = $(c.getType).val();
        data['origin'] = $(c.originType).val();

        jsonPromise(config.showReplayURI, data).then(function(retObj) {
            tasks.locals.lastReplay = retObj.task;
            let replay = '';
            let segments = retObj["gnmi_replay"];
            $(config.rpcInfoTextarea).val(segments);
            netconf.config.moduleSelect = '#ys-models'
            netconf.config.yangsetSelect = '#ys-yangset'
            let lastSegment = retObj.task.segments[retObj.task.segments.length - 1];
            fill_config(lastSegment)
            netconf.populateReplay(retObj)
        }, function(retObj) {
            popDialog("Error " + retObj.status + ": " + retObj.statusText);
        });
    }

    /**
     * Function to wait for UI element until it is loaded
     */
    async function waitForElement(selector, location = document.body) {
        return new Promise((resolve) => {
            const observer = new MutationObserver(async () => {
                if (document.querySelector(selector)) {
                    resolve(true);
                    observer.disconnect();
                }
            });
    
            observer.observe(location, {
                childList: true,
                subtree: true,
            });
        });
    }

    /**
     * Function to fill the configuration values in the GNMI page
     */
    function fill_config(task){
        let entries = task.yang.format
        let action = 'get'
        let get_type = 'all'
        let encoding = 'json_ietf'
        let prefix = false
        if (!( task.yang['proto-op'] == undefined || task.yang['proto-op'] == '')) {
        if (task.yang['proto-op'] == 'edit-config') {
            action = 'set'
        } else if ((task.yang['proto-op'] == 'get-config')){
            action = 'get'
        } else {
            action = task.yang['proto-op']
        }
        $('#ys-rpc-group > button').removeClass('selected')
        }
        if (!( entries['prefix'] == undefined || entries['prefix'] == '')) {
            prefix =  entries['prefix']
        }
        if (!( entries['encoding'] == undefined || entries['encoding'] == '')) {
            encoding =  entries['encoding']
        }
        if (!( entries['origin'] == undefined || entries['origin'] == '')) {
            origin =  entries['origin']
        }
        if (!( entries['get_type'] == undefined || entries['get_type'] == '')) {
            get_type = entries['get_type']
        }
        $('#gnmi-op-'+ action).addClass('selected');
        $('#ys-prefix').prop('checked', prefix)
        $("input[name=ys-encoding-type][value=" + encoding + "]").prop('checked', true)
        $("input[name=ys-get-type][value=" + get_type + "]").prop('checked', true)
    }

    /**
     * Download the GNMI RPC as a standalone Ansible script
     */
    function downloadAnsible(f_name,p_name,t_name) {
        let string_rpc = false
        let rpc_data = config.savedrpcs
        let data = {}
        if ($("#ys-gnmi-content").val() && ($("#ys-gnmi-content").hasClass("source-of-truth"))){
            string_rpc = true
            rpc_data = $("#ys-gnmi-content").val().trim()
        }
        else{
            data = rpcmanager.getRPCconfigs($(c.tree));
            let data_cnt= getXpathValues(data);
            rpc_data = data_cnt
        }
        if (rpc_data == ""){
          popDialog(" RPC Not Found")
          return;
        }
        let file_ext = f_name.split('.').pop()
        let file_name = f_name
        if ((file_ext == 'yaml') || (file_ext == 'yml')){
            file_name = f_name
        } else if (f_name.includes('.')){
            file_name = f_name.substr(0, f_name.lastIndexOf(".")) + '.yaml'
        } else {
            file_name = f_name + '.yaml'
        }
        let origin = "";
        origin = $(c.originType).val();
        if (origin == 'other') {
            origin = $(c.otherOrigin).val();
        }
        data['origin'] = origin;
        data['prefix'] = $(c.prefixSupport).prop("checked");
        data['base64'] = $(c.base64).prop("checked");
        data['run'] = true;
        data['encoding'] = $(c.encodingType).val();
        data['action'] = $(config.rpcOpGroup + ' .selected').attr('data-value');
        if (data['action'] == 'get') {
            data['get_type'] = $(c.getType).val();
        } else if (data['action'] == 'subscribe') {
            data['request_mode'] =  $(c.subscribeMode).val();
            data['sub_mode'] =  $(c.subscribeSubMode).val();
            data['sample_interval'] =  $(c.sampleInterval).val();
        }
        data['cfgd'] = rpc_data,
        data['string_rpc'] = string_rpc,
        data['p_name'] = p_name,
        data['t_name'] = t_name

        $.when(jsonPromise(config.getAnsibleURI, data)).then(function(retObj) {
            let element = document.createElement("a");
            let ansible_data = retObj.reply
            element.setAttribute('href', 'data:text/x-yaml;charset=utf-8,' +
                                 encodeURIComponent(ansible_data));
            element.setAttribute('download', file_name);
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        }, function(retObj) {
            popDialog("Error " + retObj.status + ": " + retObj.statusText);
        });
    };

    /**
     * Open the dialog box for "Ansible Playbook settings" values.
     *
     */
    function getAnsibleDialog() {
        fillAnsibleDialog();
        $(config.ansibledialog)
            .dialog({
                title: "Ansible Playbook Settings",
                minHeight: 222,
                minWidth: 760,
                buttons: {
                    "Download Playbook": function () {
                      let f_name = "ansible.yaml"
                      let p_name = "gNMI playbook"
                      let t_name = "gNMI RPC"
                      if($("#ys-ansible-file-name").val() != ""){
                          f_name = $("#ys-ansible-file-name").val()
                      }
                      if($("#ys-ansible-play-name").val() != ""){
                          p_name = $("#ys-ansible-play-name").val()
                      }
                      if($("#ys-ansible-task-name").val() != ""){
                          t_name = $("#ys-ansible-task-name").val()
                      }
                      downloadAnsible(f_name, p_name, t_name)
                    },
                    "Cancel": function () {
                        $(this).dialog("close")
                    }
                }
            });
    }
    /**
     * Helper function to getAnsibleDialog() and getSaveDialog().
     */
    function fillAnsibleDialog(task) {
        let dialogHtml = $("<div>");
        dialogHtml
            .append($('<div class="form-group label--inline">')
                    .append($('<div class="form-group__text">')
                            .append('<label for="ys-ansible-name">Ansible file name</label>')
                              .append('<input type=text id="ys-ansible-file-name" placeholder="ansible.yaml"/>')))
            .append($('<div class="form-group label--inline">')
                    .append($('<div class="form-group__text">')
                            .append('<label for="ys-ansible-name">Ansible playbook name</label>')
                              .append('<input type=text id="ys-ansible-play-name" placeholder="gNMI playbook" />')))
            .append($('<div class="form-group label--inline">')
                    .append($('<div class="form-group__text">')
                            .append('<label for="ys-ansible-name">Ansible  task name</label>')
                              .append('<input type=text id="ys-ansible-task-name" placeholder="gNMI RPC"/>')))

        $(config.ansibledialog).empty().html(dialogHtml);
    }
    /**
     * Public API.
     */
    return {
        config:config,
        buildJSON: buildJSON,
        runGNMI: runGNMI,
        stopSession: stopSession,
        runCapabilities: runCapabilities,
        runReplay: runReplay,
        showReplay: showReplay,
        getAnsibleDialog:getAnsibleDialog,
        downloadAnsible:downloadAnsible,
        waitForElement:waitForElement,
    };
}();
