--[[
 * ReaScript Name: Import SRT
 * Description: Imports SRT subtitles file as Text items
 * Instructions: Note that the initial cursor position is very important 
 * Author: HeDa
 * Author URl: http://forum.cockos.com/member.php?u=47822
 * Version: 0.3 beta
 * Repository: 
 * Repository URl: 
 * File URl: 
 * License: GPL v3
 * Forum Thread:
 * Forum Thread URl: 
 * REAPER: 5.0
 * Extensions: 
 

]]

------------------- OPTIONS ----------------------------------
-- this script has no options


----------------------------------------------- End of Options
 

	dbug_flag = 1 -- set to 0 for no debugging messages, 1 to get them
	function dbug (text) 
		if dbug_flag==1 then  
			if text then
				reaper.ShowConsoleMsg(text .. '\n')
			else
				reaper.ShowConsoleMsg("nil")
			end
		end
	end



	function HeDaSetNote(item,newnote)  -- HeDa - SetNote v1.0
		--ref: Lua: boolean retval, string str reaper.GetSetItemState(MediaItem item, string str)
		retval, s = reaper.GetSetItemState(item, "")	-- get the current item's chunk
		--dbug("\nChunk=" .. s .. "\n")
		has_notes = s:find("<NOTES")  -- has notes?
		if has_notes then
			-- there are notes already
			chunk, note, chunk2 = s:match("(.*<NOTES\n)(.*)(\n>\nIMGRESOURCEFLAGS.*)")
			newchunk = chunk .. newnote .. chunk2
			-- dbug(newchunk .. "\n")
			
		else
			--there are still no notes
			chunk,chunk2 = s:match("(.*IID%s%d+)(.*)")
			newchunk = chunk .. "\n<NOTES\n" .. newnote .. "\n>\nIMGRESOURCEFLAGS 0" .. chunk2
			-- dbug(newchunk .. "\n")
		end
		reaper.GetSetItemState(item, newchunk)	-- set the new chunk with the note
	end



----------------------------------------------------------------------
function CreateTextItem(starttime, endtime, notetext)

	--ref: Lua: number startOut retval, number endOut reaper.GetSet_LoopTimeRange(boolean isSet, boolean isLoop, number startOut, number endOut, boolean allowautoseek)
	reaper.GetSet_LoopTimeRange(1,0,starttime,endtime,0)	-- define the time range for the empty item
	
	--ref: Lua:  reaper.Main_OnCommand(integer command, integer flag)
	reaper.Main_OnCommand(40142,0) -- insert empty item
	
	--ref: Lua: MediaItem reaper.GetSelectedMediaItem(ReaProject proj, integer selitem)
	item = reaper.GetSelectedMediaItem(0,0) -- get the selected item
	reaper.SetMediaItemPosition(item, starttime, true)
	reaper.SetMediaItemLength(item, endtime-starttime, true)
	
	HeDaSetNote(item, notetext) -- set the note  add | character to the beginning of each line. only 1 line for now.
	
	reaper.SetEditCurPos(endtime, 1, 0)	-- moves cursor for next item
end

function ReadFile(which)
  if reaper.file_exists(which) then 
       local f = io.open(which)
       local file = {}
       local k = 1
       for line in f:lines() do
        file[k] = line
        k = k + 1
       end
       f:close()
       return file
  else 
    return nil
  end
end

function read_lines(filepath)
	reaper.PreventUIRefresh(-1) -- prevent refreshing
	
	reaper.Undo_BeginBlock() -- Begin undo group
	
	
	initialtime = reaper.GetCursorPosition();	-- store initial cursor position as time origin 00:00:00
	items={}
	lines={}
	srtfile = ReadFile(filepath)
    if srtfile then 
		local num=0
		for f, s in ipairs(srtfile) do
			if s~=nil then
				if string.find(s,'-->') then
					--00:04:22,670 --> 00:04:26,670
					sh, sm, ss, sms, eh, em, es, ems = s:match("(.*):(.*):(.*),(.*)%-%->(.*):(.*):(.*),(.*)")
					if sh then
						positionStart = tonumber(sh)*3600 + tonumber(sm)*60 + tonumber(ss) + (tonumber(sms)/1000)
						positionEnd = tonumber(eh)*3600 + tonumber(em)*60 + tonumber(es) + (tonumber(ems)/1000)
						table.insert(items, {["positionStart"]=positionStart, ["positionEnd"]=positionEnd, ["lines"]={},})
						num=num+1
						endsub=nil
						i=0
						while not endsub and i<10 do 
							i=i+1
							line=srtfile[f+i]
							if line~="\r" and line~="\n" and line~="" and line~="\r\n" then 
								table.insert(items[num].lines, line)
							else
								endsub=true
							end
						end
				
					end
				end
			end
		end
		local  numcount=0
		for j,k in ipairs(items) do 
			local textline = ""
			for a,line in ipairs(k.lines) do 
				textline = textline .. "|" .. line .. "\n"
			end
			CreateTextItem(k.positionStart + initialtime, k.positionEnd + initialtime, textline)
			numcount=numcount+1
		end
		
		if initialtime>0 then
			--warn user about imported with offset time
			reaper.ShowMessageBox("Warning: Imported ".. numcount.."items with an offset of ".. initialtime.." seconds\nIf you don't want the offset, make sure your edit cursor is at position 0 before importing.","Information",0)
		end
	end
	
	
	
	
	--[[
	local f = io.input(filepath)
	repeat
	  s = f:read ("*l") -- read one line
	  if s then  -- if not end of file (EOF)
	   -- dbug("\nline = " .. s) -- print that line
		if string.find(s,'-->') then
			
			--00:04:22,670 --> 00:04:26,670
			sh, sm, ss, sms, eh, em, es, ems = s:match("(.*):(.*):(.*),(.*)%-%->(.*):(.*):(.*),(.*)")
			if sh then
				positionStart = tonumber(sh)*3600 + tonumber(sm)*60 + tonumber(ss) + (tonumber(sms)/1000)
				positionEnd = tonumber(eh)*3600 + tonumber(em)*60 + tonumber(es) + (tonumber(ems)/1000)
				-- dbug ("positionStart=" .. positionStart)
				-- dbug ("positionEnd=" .. positionEnd)
				textline = ''
				repeat 
					line = f:read ("*l") -- read next line with the text
					dbug(line)
					if line then 
						if line ~= "" then textline = textline .. "|" .. line .. "\n"; end; 
					else 
						line=""
					end
				until line==""
				-- dbug ("textline=" .. textline)
				-- CreateTextItem(positionStart+initialtime, positionEnd+initialtime, textline);  --creates the text item
			end
			
		end
	  end
	until not s  -- until end of file

	f:close()
	--]]
	
	reaper.Main_OnCommand(40020,0) -- remove time selection
	reaper.Main_OnCommand(40289,0) -- unselect all items
	
	--ref: reaper.SetEditCurPos(number time, boolean moveview, boolean seekplay)
	reaper.SetEditCurPos(initialtime, 1, 1) -- move cursor to original position before running script
	
	
	
	--ref: Lua:  reaper.Undo_EndBlock(string descchange, integer extraflags)
	reaper.Undo_EndBlock("import SRT subtitles", 0) -- End undo group
	
	reaper.PreventUIRefresh(1) -- can refresh again
end



-- START -----------------------------------------------------
if reaper.APIExists("JS_Dialog_BrowseForOpenFiles") then 
	retval, filetxt = reaper.JS_Dialog_BrowseForOpenFiles("Select SRT file to import", "", "", "SRT files\0*.srt;*.SRT\0All files (*.*)\0*.*\0\0", false)
else
	--ref: Lua: boolean retval, string filenameNeed4096 reaper.GetUserFileNameForRead(string filenameNeed4096, string title, string defext)
	retval, filetxt = reaper.GetUserFileNameForRead("", "Select SRT file", "srt") --ref: boolean retval, string filenameNeed4096 reaper.GetUserFileNameForRead(string filenameNeed4096, string title, string defext)
end

if retval then 
	
	read_lines(filetxt);
	
else
	--ref: Lua: integer reaper.ShowMessageBox(string msg, string title, integer type)
	-- type 0=OK,1=OKCANCEL,2=ABORTRETRYIGNORE,3=YESNOCANCEL,4=YESNO,5=RETRYCANCEL : ret 1=OK,2=CANCEL,3=ABORT,4=RETRY,5=IGNORE,6=YES,7=NO
	reaper.ShowMessageBox("Cancelled and nothing was imported into REAPER","Don't worry",0)
end
