! trace A ->Memory ecard (FILE$)
! Memory card (FILE$) ->trace B
INTEGER T1(701),T2(701)
!
GOSUB *SETUP                                                    ! Set up
GOSUB *FSAVE                                                    ! Save the data in the memory card.
GOSUB *FLOAD                                                    ! Load the data from the memory card.
STOP
!
*SETUP
    OUTPUT 31;"VS2":CLS
    PRINT "##### OPEN/CLOSE #####"
    BUZZER 1000,500
    CURSOR 5,5:PRINT "> >Please, write protect switch is off !"
    CURSOR 5,7:INPUT "> >Save file name = ?", FILE$
                                                                ! Input the file name.
    CURSOR 5,9:INPUT "> >New file ? (Y=1/N=0) ",NEW
    IF NEW=0 THEN PURGE FILE$                                   ! Current file is deleted.
    OUTPUT 31;"IP VS1":CLS
    OUTPUT 31;"CLN CF30MZ SP1MZ RE-10DB RB100KZ"
    RETURN
*FSAVE
    OUTPUT 31;"VS1":CLS
    BUZZER 500,500
    PRINT "trace A ->Card saving .. (file) = ",FILE$
    OPEN FILE$ FOR OUTPUT AS #FD;ASCII
                                                                ! Open the file.
    OUTPUT 31; "GTA"                                            ! Read trace A.
    FOR I=1 TO 701
        T1(I)=RTRACE(I-1,0)                                     ! Save the data in the variables.
        OUTPUT #FD;T1(I)                                        ! Save the data in the memory card.
    NEXT I
    CLOSE #FD                                                   ! Close the file.
    OUTPUT 31; "AB"                                             ! A blank
    CLS;BUZZER 500,500
    RETURN
*FLOAD
    OUTPUT 31;"VS1":CLS
    BUZZER 500,500
    OUTPUT 31;"CWB BY"                                          ! B clear & view
    CLS:PRINT "Card loading .. ->trace B (file) = ",FILE$
    OPEN FILE$ FOR INPUT AS #FD;ASCII
                                                                ! Open the file.
    FOR I=1 TO 701
        ENTER #FD;T2(1)                                         ! Load the data from the memory card.
        WTRACE(T2(1),I-1,1)}                                    ! Write the data in the work area.
    NEXT I
    OUTPUT 31;"PTB"                                             ! Write the data in trace B.
    OUTPUT 31;"BY"                                              ! B view
    CLOSE #FD                                                   ! Close the file.
    CLS:BUZZER 500,500
    RETURN