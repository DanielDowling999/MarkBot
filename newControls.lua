Keys = { 
    [C.GBA_KEY.A] = "A", 
    [C.GBA_KEY.B] = "B", 
    [C.GBA_KEY.SELECT] = "SELECT", 
    [C.GBA_KEY.START] = "START", 
    [C.GBA_KEY.RIGHT] = "RIGHT", 
    [C.GBA_KEY.LEFT] = "LEFT", 
    [C.GBA_KEY.UP] = "UP", 
    [C.GBA_KEY.DOWN] = "DOWN", 
    [C.GBA_KEY.R] = "R", 
    [C.GBA_KEY.L] = "L" 
}
local next_frame = 30
function frame_callback()
    next_frame = next_frame-1
    if next_frame > 0 then
        return
    end
    next_frame = 30
end



function pressButton(button, n_times, delay)
    n_times = n_times or 1
    delay = delay or 0.2
    --Inputs are performed with addKey(key). This holds the button down until clearKey is used.
    --clearKey should be used a frame after a button press, and then a delay of about ten frames before the next input. Probably overshoot.
    while(n_times > 0)
    do
        emu:addKey(button)
        callbacks:oneshot('frame', frame_callback)
        emu:clearKey(button)
        wait = 10
        while(wait > 0)
        do 
            callbacks:oneshot('frame', frame_callback)
        end
        n_times = n_times-1
        
    end
