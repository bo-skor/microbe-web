#!/usr/bin/haserl
<%in p/common.cgi %>
<%
plugin="telegrambot"
plugin_name="Telegram Bot"
page_title="Telegram Bot"

params="enabled token"
for i in 0 1 2 3 4 5 6 7 8 9; do
  params="${params} command_${i} description_${i} script_${i}"
done

tmp_file=/tmp/${plugin}.conf

config_file="${ui_config_dir}/${plugin}.conf"
[ ! -f "$config_file" ] && touch $config_file

if [ "POST" = "$REQUEST_METHOD" ]; then
  # parse values from parameters
  for _p in $params; do
    eval ${plugin}_${_p}=\$POST_${plugin}_${_p}
    sanitize "${plugin}_${_p}"
  done; unset _p

  ### Validation
  if [ "true" = "$telegrambot_enabled" ]; then
    [ -z "$telegrambot_token" ] &&
      flash_append "danger" "Telegram token cannot be empty." &&
      error=11
  fi

  if [ -z "$error" ]; then
    # create temp config file
    :>$tmp_file
    for _p in $params; do
      echo "${plugin}_${_p}=\"$(eval echo \$${plugin}_${_p})\"" >>$tmp_file
    done; unset _p
    mv $tmp_file $config_file

    update_caminfo

    /etc/init.d/S93telegrambot restart >/dev/null

    redirect_back "success" "${plugin_name} config updated."
  fi

  redirect_to $SCRIPT_NAME
else
  include $config_file

  for _p in $params; do
    sanitize4web "${plugin}_${_p}"
  done; unset _p

  # Default values
  [ -z "$telegrambot_caption" ] && telegrambot_caption="%hostname, %datetime"
fi
%>
<%in p/header.cgi %>

<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 row-cols-xl-1 g-4 mb-4">
  <div class="col">
    <form action="<%= $SCRIPT_NAME %>" method="post">
      <% field_switch "telegrambot_enabled" "Enable Telegram Bot" %>

      <div class="input-group mb-3">
        <input type="text" id="telegrambot_token" name="telegrambot_token" value="<%= $telegrambot_token %>"
          class="form-control" placeholder="Bot Token" aria-label="Your Telegram Bot authentication token.">
        <span class="input-group-text">
          <button type="button" class="btn" data-bs-toggle="modal" data-bs-target="#helpModal">Help</button>
        </span>
      </div>
      <div class="bot-commands mb-4">
        <h5>Bot Commands</h5>
        <p class="hint mb-3">Use $chat_id variable for the active chat ID.</p>
        <% for i in 0 1 2 3 4 5 6 7 8 9; do %>
        <div class="row g-1 mb-3 mb-lg-1">
          <div class="col-4 col-lg-2">
            <input type="text" id="telegrambot_command_<%= $i %>" name="telegrambot_command_<%= $i %>"
              class="form-control" placeholder="Bot Command" value="<%= $(t_value "telegrambot_command_$i") %>">
            </div>
          <div class="col-8 col-lg-3">
            <input type="text" id="telegrambot_description_<%= $i %>" name="telegrambot_description_<%= $i %>"
              class="form-control" placeholder="Command Description" value="<%= $(t_value "telegrambot_description_$i") %>">
            </div>
          <div class="col-lg-7">
            <input type="text" id="telegrambot_script_<%= $i %>" name="telegrambot_script_<%= $i %>"
              class="form-control" placeholder="Linux Command" value="<%= $(t_value "telegrambot_script_$i") %>">
          </div>
        </div>
        <% done %>
      </div>
      <button type="button" class="btn btn-danger float-end" id="reset_commands">Reset commands</button>
      <% button_submit %>
    </form>
  </div>
</div>

<div class="ui-expert">
  <% ex "cat $config_file" %>
  <% button_webui_log %>
</div>

<div class="modal fade" id="helpModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">To create a Telegram bot</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <ol>
          <li>Start a chat with <a href=\"https://t.me/BotFather\">@BotFather</a></li>
          <li>Enter <code>/start</code> to start a session.</li>
          <li>Enter <code>/newbot</code> to create a new bot.</li>
          <li>Give your bot channel a name, e.g. <i>cool_cam_bot</i>.</li>
          <li>Give your bot a username, e.g. <i>CoolCamBot</i>.</li>
          <li>Copy the token assigned to your new bot by the BotFather, and paste it to the form.</li>
        </ol>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
</div>

<script>
const default_commands = [
  {command:'start',script:'echo "Hello"',description:'Start conversation'},
  {command:'help',script:'echo "Try https://t.me/openipc"',description:'Request help'},
  {command:'info',script:'cat /etc/os-release',description:'Information about system'},
  {command:'snap',script:'snapshot4cron.sh && send2telegram.sh -c $chat_id -p /tmp/snapshot4cron.jpg -i',description:'Take a snapshot'},
  {command:'stop',script:'/etc/init.d/S93telegrambot stop',description:'Stop the bot'},
  {command:'wall',script:'send2openwall.sh && send2telegram.sh -c $chat_id -m "Sent to OpenWall"',description:'Send snapshot to OpenWall'},
  {command:'yadisk',script:'send2yadisk.sh && send2telegram.sh -c $chat_id -m "Sent to Yandex Disk"',description:'Send snapshot to Yandex Disk'},
  {command:'restart',script:'/etc/init.d/S93telegrambot restart',description:'Restart the bot'},
]
function resetBotCommands() {
  $$('.bot-commands input[type=text]').forEach(e => e.value = '');
  let i=0;
  default_commands.forEach(c => {
    $('#telegrambot_command_'+i).value = c.command;
    $('#telegrambot_script_'+i).value = c.script;
    $('#telegrambot_description_'+i).value = c.description;
    i++;
  });
}
$('#reset_commands').addEventListener('click', resetBotCommands);
</script>

<%in p/footer.cgi %>
