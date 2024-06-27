<fieldset class="sql">
  <textarea class="sqlcode" name="{{name}}" spellcheck="false">
% include('attrs')
  </textarea>
  <button type="button">Execute</button>
% if defined('points') and points>0:
  <span class="points">{{points}} points</span>
% end
  <button type="button">Minimize Output</button>
  <div class="sqlbusy"></div>
  <div class="sqloutput"></div>
</fieldset>
