drop schema if exists `evereye`;
create schema `evereye`;
USE `evereye`;

create table `users` (
`userID` int AUTO_INCREMENT PRIMARY KEY,
`keyID` varchar(20) UNIQUE,
`firstName` char(64) NOT NULL,
`lastName` char(64) NOT NULL,
`userPassword` varchar(20) NOT NULL)
ENGINE=INNODB;

create table `locks` (
`lockID` int NOT NULL PRIMARY KEY,
`lockName` char(64) NOT NULL)
ENGINE=INNODB;

create table `log` (
`logID` int AUTO_INCREMENT PRIMARY KEY,
`userID` int NOT NULL,
`logDate` date NOT NULL,
`logTime` time NOT NULL,
`lockID` int NOT NULL,
`authenticated` boolean NOT NULL,
FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
FOREIGN KEY (`lockID`) REFERENCES `locks`(`lockID`));

create table `lockPermissions` (
`userID` int NOT NULL,
`lockID` int NOT NULL,
FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
FOREIGN KEY (`lockID`) REFERENCES `locks`(`lockID`),
PRIMARY KEY (`userID`, `lockID`));

CREATE VIEW logView AS SELECT logID, firstName, lastName, logDate, logTime, lockName, authenticated FROM log
JOIN users ON log.userID = users.userID JOIN locks on log.lockID = locks.lockID;

insert into locks(lockID, lockName)
values (1, "Primary"),
(2, "Secondary");

insert into users(keyID, firstName, lastName, userPassword)
values (null, "Unregistered", "User", ""),
(null, "Deleted", "User", "");