'use strict';

// Configuration parameters

const PhotoFrameFolderId = "1JjuczUEUqgWIq05_cPnL-g8_HwSW-YD1";
const DownloadDirectory = "./files"; //eg., /home/pi/gdrive-photo-frame
var privatekey = require('./privatekey.json');
const BATCH_SIZE = 1;


// code

const { google } = require('googleapis');
var async = require("async");
var Batch = require('batch'),
    batch = new Batch;

const fs = require('fs');
const os = require('os');
const uuid = require('uuid');
const path = require('path');

var prevDownloadFiles = [];
var prevDownloadFilesWithExtn = [];
var filesToDownload = [];
var filedInSharedDrive = [];
var filedDownloaded = [];
var filesToDelete = [];


let jwtClient = new google.auth.JWT(
    privatekey.client_email,
    null,
    privatekey.private_key, [
        'https://www.googleapis.com/auth/drive'
    ]);

var drive = null;
console.log("N-GDrive: Starting at %s\n", new Date());

//authenticate request
jwtClient.authorize(function(err, tokens) {
    if (err) {
        console.log(err);
        return;
    } else {
        console.log("Successfully connected\n");
        // console.dir(tokens);
        drive = google.drive('v3');
        downloadedFiles();
        // listFiles(jwtClient);
    }
});


function downloadedFiles() {
    prevDownloadFiles = [];
    fs.readdirSync(DownloadDirectory).forEach(file => {
        prevDownloadFilesWithExtn.push(file);
        let extn = path.extname(file);
        let fname = path.basename(file, extn);
        // console.log(fname);
        prevDownloadFiles.push(fname);
    });
    console.log(`Previously downloaded Files: ${prevDownloadFiles.length} \n`);
    // console.dir(prevDownloadFiles);
    listFiles(jwtClient);
}

function listFiles(auth) {
    var pageToken = null;
    async.doWhilst(function(callback) {
        drive.files.list({
            fields: 'nextPageToken, files',
            spaces: 'drive',
            auth: auth,
            q: "'" + PhotoFrameFolderId + "' in parents and (mimeType contains 'image/' or mimeType contains 'video/')",
            pageSize: 999,
            pageToken: pageToken
        }, function(err, res) {
            if (err) {
                // Handle error
                console.error(err);
                callback(err)
            } else {
                // console.dir(res);
                res.data.files.forEach(function(file) {
                    // console.log('%s (id: %s, parent:%s, mime:%s, modified:%s)', file.name, file.id, file.parents, file.mimeType, file.modifiedTime);
                    // console.log('%s - %s', file.name, file.md5Checksum);
                    filedInSharedDrive.push(file.md5Checksum);
                    if (prevDownloadFiles.indexOf(file.md5Checksum) != -1) {
                        console.log(`-- SKIP: ${file.name}`);
                    } else {
                        console.log(`-- DOWNLOAD: ${file.name}`);
                        filesToDownload.push(file)
                    }
                    // downloadFile(auth, file);
                });
                pageToken = res.nextPageToken;
                callback();
            }
        });
    }, function() {
        return !!pageToken;
    }, function(err) {
        if (err) {
            // Handle error
            console.error(err);
        } else {
            // All pages fetched
            // console.log("\nAll page fetched");
            if (!filesToDownload.length) {
                deleteRemovedFiles(prevDownloadFiles, filedInSharedDrive);
                console.log("\nN-GDrive: No new files to download.");
                return;
            }

            console.log("\nTo download %s file(s)\n", filesToDownload.length);

            batch.concurrency(BATCH_SIZE);
            filesToDownload.reverse();
            filesToDownload.forEach(function(file) {
                batch.push(function(done) {
                    downloadFile(auth, file, done);
                })
            });

            batch.on('progress', function(e) {
                console.log("---- %s of %s completed", e.complete, e.total);
            });


            batch.end(function(err, files) {
                if (err) {
                    console.log('error in batch done')
                    console.log(err);
                } else {
                    deleteRemovedFiles(prevDownloadFiles, filedInSharedDrive);
                    console.log("\nN-GDrive: All files downloaded successfully");
                }
            });
        }
    });
}


function deleteRemovedFiles(prevDownloadFiles, filedInSharedDrive) {
    filesToDelete = prevDownloadFiles.filter(n => (filedInSharedDrive.indexOf(n) == -1));
    if (filesToDelete.length) {
        console.log(`\n${filesToDelete.length} file(s) to be deleted\n`);
        var fname = '';
        filesToDelete.forEach(function (file) {
            fname = prevDownloadFilesWithExtn[prevDownloadFiles.indexOf(file)];
            var fPath = path.join(DownloadDirectory, fname);
            console.log('-- DELETE ' + fPath);
            fs.unlinkSync(fPath);
        });
    }
    else {
        console.log('\nNo files were deleted in shared drive');
    }
}


function downloadFile(auth, file, callback) {
    console.log('--- Going to download: [%s]', file.name);
    const fileId = file.id;
    // ""+file.name+"-MD5-"+file.md5Checksum
    const filePath = path.join(DownloadDirectory, file.md5Checksum + "." + file.fileExtension);
    // console.log(`writing to ${filePath}`);
    const dest = fs.createWriteStream(filePath);

    drive.files.get({
            fileId: fileId,
            auth: auth,
            alt: 'media'
        }, { responseType: 'stream' },
        function(err, res) {
            if (err) {
                console.log("Error for file %s: ", file.name);
                // console.dir(err);
                fs.unlinkSync(filePath);
                callback();
                return;
            }
            // console.dir(res.data);
            if (typeof(res.data) != 'undefined') {
                res.data
                    .on('end', () => {
                        console.log('--- DONE -> %s - %s', file.name, file.md5Checksum);
                        const stats = fs.statSync(filePath);
                        const fileSizeInBytes = stats.size;
                        if (fileSizeInBytes < 5) { // to handle 0 bytes file error; safe to be 5 bytes
                            console.log('Deleteing incomplete file %s', file.md5Checksum);
                            fs.unlinkSync(filePath);

                        }
                        callback();
                    })
                    .on('error', err => {
                        console.log('Error', err);
                        fs.unlinkSync(filePath);
                        callback();
                    })
                    .pipe(dest);
            }

        }
    );



}


/*
Options

"mimeType='image/png'"
// mimeType='image/jpeg'
// mimeType='image/png'
// 1JjuczUEUqgWIq05_cPnL-g8_HwSW-YD1

modifiedTime > '2012-06-04T12:00:00' and (mimeType contains 'image/' or mimeType contains 'video/')

*/